#!/bin/bash
# Launch AION on Shadeform ephemeral GPU instance

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 AION GPU Instance Launcher${NC}"

# Default values
GPU_TYPE="${GPU_TYPE:-A100}"
GPU_COUNT="${GPU_COUNT:-1}"
CLOUD="${CLOUD:-nebius}"
REGION="${REGION:-us-central1}"
INSTANCE_NAME="aion-$(date +%Y%m%d-%H%M%S)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --gpu-type)
            GPU_TYPE="$2"
            shift 2
            ;;
        --gpu-count)
            GPU_COUNT="$2"
            shift 2
            ;;
        --cloud)
            CLOUD="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --name)
            INSTANCE_NAME="$2"
            shift 2
            ;;
        --auto-delete)
            AUTO_DELETE="true"
            shift
            ;;
        --help)
            cat << EOF
Usage: $0 [OPTIONS]

Options:
    --gpu-type TYPE      GPU type (A100, H100, H200, etc.) [default: A100]
    --gpu-count COUNT    Number of GPUs [default: 1]
    --cloud PROVIDER     Cloud provider [default: nebius]
    --region REGION      Cloud region [default: us-central1]
    --name NAME          Instance name [default: auto-generated]
    --auto-delete        Enable auto-deletion after job completion
    --help               Show this help message

Examples:
    # Launch with 8x H200 GPUs
    $0 --gpu-type H200 --gpu-count 8

    # Launch with auto-delete
    $0 --gpu-type A100 --gpu-count 4 --auto-delete

EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Load configuration
if [ ! -f .shadeform_config ]; then
    echo -e "${RED}❌ Configuration not found. Run deploy_shadeform.sh first.${NC}"
    exit 1
fi

source .shadeform_config

# Validate API key
if [ -z "$SHADEFORM_API_KEY" ]; then
    echo -e "${RED}❌ SHADEFORM_API_KEY not set${NC}"
    exit 1
fi

# Determine shade instance type based on GPU
case "${GPU_TYPE}" in
    H200)
        SHADE_TYPE="H200"
        ;;
    H100)
        SHADE_TYPE="H100"
        ;;
    A100)
        SHADE_TYPE="A100"
        ;;
    L40S)
        SHADE_TYPE="L40S"
        ;;
    *)
        SHADE_TYPE="${GPU_TYPE}"
        ;;
esac

# Handle multi-GPU configurations
if [ "$GPU_COUNT" -gt 1 ]; then
    SHADE_TYPE="${GPU_COUNT}x_${SHADE_TYPE}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Instance Name: ${INSTANCE_NAME}"
echo -e "  GPU Type:      ${GPU_TYPE} x${GPU_COUNT}"
echo -e "  Cloud:         ${CLOUD}"
echo -e "  Region:        ${REGION}"
echo -e "  Template:      ${TEMPLATE_ID}"
echo -e "  Volume:        ${VOLUME_ID}"
echo -e "  Auto-delete:   ${AUTO_DELETE:-false}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Launch instance
echo -e "\n${BLUE}Launching instance...${NC}"

LAUNCH_RESPONSE=$(curl -s --request POST "https://api.shadeform.ai/v1/instances/create" \
  -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
        \"template_id\": \"${TEMPLATE_ID}\",
        \"cloud\": \"${CLOUD}\",
        \"region\": \"${REGION}\",
        \"shade_instance_type\": \"${SHADE_TYPE}\",
        \"shade_cloud\": true,
        \"name\": \"${INSTANCE_NAME}\",
        \"volume_ids\": [\"${VOLUME_ID}\"]
      }")

if echo "$LAUNCH_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    INSTANCE_ID=$(echo "$LAUNCH_RESPONSE" | jq -r '.id')
    echo -e "${GREEN}✅ Instance launched: ${INSTANCE_ID}${NC}"
else
    echo -e "${RED}❌ Failed to launch instance${NC}"
    echo "$LAUNCH_RESPONSE" | jq '.'
    exit 1
fi

# Save instance info
cat > .current_instance << EOF
INSTANCE_ID=${INSTANCE_ID}
INSTANCE_NAME=${INSTANCE_NAME}
LAUNCH_TIME=$(date -Iseconds)
GPU_TYPE=${GPU_TYPE}
GPU_COUNT=${GPU_COUNT}
EOF

# Poll for instance to become active
echo -e "\n${BLUE}Waiting for instance to become active...${NC}"

MAX_WAIT=600  # 10 minutes
WAIT_TIME=0
POLL_INTERVAL=10

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
        "https://api.shadeform.ai/v1/instances/${INSTANCE_ID}/info")
    
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // .instance.status // "unknown"')
    
    case "$STATUS" in
        "active"|"running")
            echo -e "\n${GREEN}✅ Instance is active!${NC}"
            
            # Get connection details
            IP=$(echo "$STATUS_RESPONSE" | jq -r '.ip // .instance.ip // "N/A"')
            SSH_USER=$(echo "$STATUS_RESPONSE" | jq -r '.ssh_user // .instance.ssh_user // "ubuntu"')
            SSH_PORT=$(echo "$STATUS_RESPONSE" | jq -r '.ssh_port // .instance.ssh_port // 22')
            
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}🎉 AION GPU INSTANCE READY!${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "Instance ID:   ${YELLOW}${INSTANCE_ID}${NC}"
            echo -e "Instance Name: ${YELLOW}${INSTANCE_NAME}${NC}"
            echo -e "IP Address:    ${YELLOW}${IP}${NC}"
            echo -e "SSH Access:    ${YELLOW}ssh ${SSH_USER}@${IP} -p ${SSH_PORT}${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${CYAN}AION API will be available at:${NC}"
            echo -e "  ${YELLOW}http://${IP}:30001${NC}"
            echo ""
            echo -e "${CYAN}To check AION status:${NC}"
            echo -e "  ${YELLOW}curl http://${IP}:30001/status${NC}"
            echo ""
            echo -e "${CYAN}To monitor logs:${NC}"
            echo -e "  ${YELLOW}./scripts/monitor_instance.sh${NC}"
            echo ""
            echo -e "${CYAN}To delete instance:${NC}"
            echo -e "  ${YELLOW}./scripts/delete_instance.sh${NC}"
            echo ""
            
            # Save connection info
            cat >> .current_instance << EOF
IP=${IP}
SSH_USER=${SSH_USER}
SSH_PORT=${SSH_PORT}
API_URL=http://${IP}:30001
EOF
            
            exit 0
            ;;
        "pending"|"provisioning"|"starting")
            echo -ne "\r${YELLOW}⏳ Status: ${STATUS} (${WAIT_TIME}s)...${NC}"
            ;;
        "error"|"failed")
            echo -e "\n${RED}❌ Instance failed to start${NC}"
            echo "$STATUS_RESPONSE" | jq '.'
            exit 1
            ;;
        *)
            echo -ne "\r${YELLOW}⏳ Waiting... Status: ${STATUS} (${WAIT_TIME}s)${NC}"
            ;;
    esac
    
    sleep $POLL_INTERVAL
    WAIT_TIME=$((WAIT_TIME + POLL_INTERVAL))
done

echo -e "\n${RED}❌ Timeout waiting for instance to become active${NC}"
exit 1