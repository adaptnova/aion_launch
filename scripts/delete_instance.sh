#!/bin/bash
# Delete AION Shadeform instance (preserves volume)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ ! -f .current_instance ]; then
    echo -e "${RED}❌ No current instance found${NC}"
    exit 1
fi

source .current_instance

echo -e "${YELLOW}⚠️  About to delete instance: ${INSTANCE_NAME}${NC}"
echo -e "${BLUE}Instance ID: ${INSTANCE_ID}${NC}"
echo -e "${GREEN}Note: The persistent volume will be preserved${NC}"
echo ""
read -p "Are you sure? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled${NC}"
    exit 0
fi

# Trigger final S3 sync
echo -e "${BLUE}Triggering final S3 sync...${NC}"
curl -s -X POST "${API_URL}/system/command" \
    -H "Content-Type: application/json" \
    -d '{"command": "bash", "args": ["-c", "cd /opt/aion && ./entrypoint.sh sync_to_s3"]}' \
    2>/dev/null || echo -e "${YELLOW}Warning: Could not trigger final sync${NC}"

sleep 5

# Delete instance
echo -e "${BLUE}Deleting instance...${NC}"

DELETE_RESPONSE=$(curl -s --request POST "https://api.shadeform.ai/v1/instances/${INSTANCE_ID}/delete" \
    -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
    -H "Content-Type: application/json")

if echo "$DELETE_RESPONSE" | jq -e '.success // true' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Instance deleted successfully${NC}"
    
    # Archive instance info
    mv .current_instance ".archived_instance_$(date +%Y%m%d_%H%M%S)"
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Instance terminated. Volume preserved for next run.${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}❌ Failed to delete instance${NC}"
    echo "$DELETE_RESPONSE" | jq '.'
    exit 1
fi