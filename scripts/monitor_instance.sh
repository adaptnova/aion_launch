#!/bin/bash
# Monitor running AION instance

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ ! -f .current_instance ]; then
    echo -e "${RED}❌ No current instance found${NC}"
    exit 1
fi

source .current_instance

echo -e "${CYAN}📊 Monitoring AION Instance: ${INSTANCE_NAME}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Function to check API status
check_api() {
    if curl -s -f "${API_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API: Online${NC}"
        
        # Get detailed status
        STATUS=$(curl -s "${API_URL}/status" | jq '.')
        echo -e "\n${CYAN}System Status:${NC}"
        echo "$STATUS" | jq -r '
            "  Mode: \(.system_state.mode)
  Trust Level: \(.system_state.trust_level)
  Restrictions: \(.system_state.restrictions)
  Active Goals: \(.active_goals)
  Safety Mode: \(.safety_status.mode)"
        '
    else
        echo -e "${RED}❌ API: Offline${NC}"
    fi
}

# Function to check GPU status
check_gpu() {
    echo -e "\n${CYAN}GPU Status:${NC}"
    GPU_STATUS=$(curl -s -X POST "${API_URL}/system/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "nvidia-smi", "args": ["--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader"]}' \
        2>/dev/null | jq -r '.stdout // "N/A"')
    
    if [ "$GPU_STATUS" != "N/A" ]; then
        echo "$GPU_STATUS" | while IFS=, read -r idx name util mem_used mem_total temp; do
            echo -e "  GPU $idx: $name - Util: ${util}% - Memory: ${mem_used}/${mem_total} - Temp: ${temp}°C"
        done
    else
        echo -e "  ${YELLOW}Unable to fetch GPU status${NC}"
    fi
}

# Function to tail logs
tail_logs() {
    echo -e "\n${CYAN}Recent Logs:${NC}"
    curl -s -X POST "${API_URL}/system/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "tail", "args": ["-n", "20", "/aion/logs/autonomy.log"]}' \
        2>/dev/null | jq -r '.stdout // "No logs available"'
}

# Function to check S3 sync status
check_s3() {
    echo -e "\n${CYAN}S3 Sync Status:${NC}"
    
    # Load S3 config
    if [ -f .shadeform_config ]; then
        source .shadeform_config
        
        # Check last sync time
        LAST_SYNC=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}outputs/" \
            --endpoint-url "${AWS_ENDPOINT_URL:-https://storage.us-central1.nebius.cloud:443}" \
            --recursive --summarize 2>/dev/null | tail -1)
        
        if [ -n "$LAST_SYNC" ]; then
            echo -e "  ${GREEN}✅ S3 Connected${NC}"
            echo -e "  Bucket: ${S3_BUCKET}/${S3_PREFIX}"
        else
            echo -e "  ${YELLOW}⚠️  No S3 data yet${NC}"
        fi
    fi
}

# Main monitoring loop
if [ "$1" = "--watch" ]; then
    # Continuous monitoring
    while true; do
        clear
        echo -e "${CYAN}📊 AION Instance Monitor - $(date)${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "Instance: ${YELLOW}${INSTANCE_NAME}${NC}"
        echo -e "ID:       ${YELLOW}${INSTANCE_ID}${NC}"
        echo -e "API URL:  ${YELLOW}${API_URL}${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        check_api
        check_gpu
        check_s3
        
        echo -e "\n${YELLOW}Press Ctrl+C to exit${NC}"
        sleep 10
    done
else
    # Single check
    check_api
    check_gpu
    check_s3
    tail_logs
    
    echo -e "\n${CYAN}For continuous monitoring:${NC}"
    echo -e "  ${YELLOW}$0 --watch${NC}"
fi