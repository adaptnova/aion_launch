#!/bin/bash
# AION Shadeform Ephemeral GPU Deployment Script
# Orchestrates disposable GPU instances with persistent S3 state

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AION Ephemeral GPU Deployment System${NC}"
echo -e "${YELLOW}⚠️  SECURITY REMINDER: Never commit credentials to git!${NC}"

# Configuration
IMAGE_NAME="aion-ephemeral"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-adaptchase}"
TAG="${TAG:-$(date +%Y.%m.%d)}"

# Step 0: Validate environment variables
echo -e "\n${BLUE}Validating environment...${NC}"

required_vars=(
    "DOCKERHUB_TOKEN"
    "SHADEFORM_API_KEY"
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    printf '%s\n' "${missing_vars[@]}"
    echo -e "\n${YELLOW}Please set these variables in your .env file:${NC}"
    cat << 'EOF'

# Docker Hub (get PAT from https://hub.docker.com/settings/security)
export DOCKERHUB_USERNAME="adaptchase"
export DOCKERHUB_TOKEN="<your-docker-pat>"

# Shadeform (from https://platform.shadeform.ai/settings/api-keys)
export SHADEFORM_API_KEY="<your-shadeform-key>"

# Nebius COS S3
export AWS_ACCESS_KEY_ID="<from-nebius>"
export AWS_SECRET_ACCESS_KEY="<from-nebius>"
export AWS_ENDPOINT_URL="https://storage.us-central1.nebius.cloud:443"
export AWS_DEFAULT_REGION="us-central1"
export S3_BUCKET="cos"
export S3_PREFIX="aion/runs/"

EOF
    exit 1
fi

echo -e "${GREEN}✅ Environment validated${NC}"

# Step 1: Build Docker image
echo -e "\n${BLUE}Building Docker image...${NC}"
cd docker
docker build -f Dockerfile.ephemeral -t "${IMAGE_NAME}:${TAG}" -t "${IMAGE_NAME}:latest" ..
echo -e "${GREEN}✅ Image built: ${IMAGE_NAME}:${TAG}${NC}"

# Step 2: Push to Docker Hub
echo -e "\n${BLUE}Pushing to Docker Hub...${NC}"
echo -n "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

docker tag "${IMAGE_NAME}:${TAG}" "docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"
docker tag "${IMAGE_NAME}:latest" "docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"

docker push "docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"
docker push "docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"

# Get image digest for pinning
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}")
echo -e "${GREEN}✅ Image pushed: ${DIGEST}${NC}"

# Step 3: Create Shadeform volume (if not exists)
echo -e "\n${BLUE}Creating Shadeform persistent volume...${NC}"

VOLUME_RESPONSE=$(curl -s --request POST "https://api.shadeform.ai/v1/volumes/create" \
  -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "cloud": "nebius",
        "region": "us-central1",
        "size_in_gb": 500,
        "name": "aion-workspace"
      }')

if echo "$VOLUME_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    VOLUME_ID=$(echo "$VOLUME_RESPONSE" | jq -r '.id')
    echo -e "${GREEN}✅ Volume created: ${VOLUME_ID}${NC}"
else
    echo -e "${YELLOW}⚠️  Volume might already exist or error occurred${NC}"
    # Try to list existing volumes
    VOLUMES=$(curl -s -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
        "https://api.shadeform.ai/v1/volumes")
    VOLUME_ID=$(echo "$VOLUMES" | jq -r '.volumes[] | select(.name=="aion-workspace") | .id' | head -1)
    if [ -n "$VOLUME_ID" ]; then
        echo -e "${GREEN}✅ Using existing volume: ${VOLUME_ID}${NC}"
    else
        echo -e "${RED}❌ Could not create or find volume${NC}"
        exit 1
    fi
fi

# Step 4: Create Shadeform template
echo -e "\n${BLUE}Creating Shadeform template...${NC}"

DOCKER_IMAGE="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
TEMPLATE_NAME="aion-ephemeral-$(date +%Y%m%d)"

TEMPLATE_RESPONSE=$(curl -s --request POST "https://api.shadeform.ai/v1/templates/save" \
  -H "X-API-KEY: ${SHADEFORM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"${TEMPLATE_NAME}\",
    \"description\": \"AION Ephemeral GPU - Full autonomy with S3 persistence\",
    \"public\": false,
    \"launch_configuration\": {
      \"type\": \"docker\",
      \"docker_configuration\": {
        \"image\": \"${DOCKER_IMAGE}\",
        \"args\": \"\",
        \"shared_memory_in_gb\": 32,
        \"envs\": [
          {\"name\": \"AWS_ACCESS_KEY_ID\",       \"value\": \"${AWS_ACCESS_KEY_ID}\"},
          {\"name\": \"AWS_SECRET_ACCESS_KEY\",   \"value\": \"${AWS_SECRET_ACCESS_KEY}\"},
          {\"name\": \"AWS_ENDPOINT_URL\",        \"value\": \"${AWS_ENDPOINT_URL:-https://storage.us-central1.nebius.cloud:443}\"},
          {\"name\": \"AWS_DEFAULT_REGION\",      \"value\": \"${AWS_DEFAULT_REGION:-us-central1}\"},
          {\"name\": \"S3_BUCKET\",               \"value\": \"${S3_BUCKET:-cos}\"},
          {\"name\": \"S3_PREFIX\",               \"value\": \"${S3_PREFIX:-aion/runs/}\"},
          {\"name\": \"AUTO_DELETE\",             \"value\": \"${AUTO_DELETE:-false}\"},
          {\"name\": \"GIT_SHA\",                 \"value\": \"$(git rev-parse HEAD 2>/dev/null || echo 'unknown')\"}
        ],
        \"volume_mounts\": [
          {\"host_path\": \"/mnt/vol\", \"container_path\": \"/workspace\"}
        ],
        \"registry_credentials\": {
          \"username\": \"${DOCKERHUB_USERNAME}\",
          \"password\": \"${DOCKERHUB_TOKEN}\"
        }
      }
    },
    \"volume_mount\": { \"auto\": true },
    \"auto_delete\": { \"date_threshold\": \"12h\" },
    \"alert\": { \"date_threshold\": \"11h\" },
    \"tags\": [\"aion\", \"ephemeral\", \"autonomous\"]
  }")

if echo "$TEMPLATE_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    TEMPLATE_ID=$(echo "$TEMPLATE_RESPONSE" | jq -r '.id')
    echo -e "${GREEN}✅ Template created: ${TEMPLATE_ID}${NC}"
else
    echo -e "${RED}❌ Failed to create template${NC}"
    echo "$TEMPLATE_RESPONSE" | jq '.'
    exit 1
fi

# Save configuration for later use
cat > .shadeform_config << EOF
# AION Shadeform Configuration
# Generated: $(date)
VOLUME_ID=${VOLUME_ID}
TEMPLATE_ID=${TEMPLATE_ID}
DOCKER_IMAGE=${DOCKER_IMAGE}
DOCKER_DIGEST=${DIGEST}
S3_BUCKET=${S3_BUCKET}
S3_PREFIX=${S3_PREFIX}
EOF

echo -e "\n${GREEN}✨ DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Volume ID:    ${YELLOW}${VOLUME_ID}${NC}"
echo -e "Template ID:  ${YELLOW}${TEMPLATE_ID}${NC}"
echo -e "Docker Image: ${YELLOW}${DOCKER_IMAGE}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}To launch an instance:${NC}"
echo -e "  ./scripts/launch_gpu_instance.sh"
echo ""
echo -e "${GREEN}To launch with 8x H200 GPUs:${NC}"
echo -e "  ./scripts/launch_gpu_instance.sh --gpu-type H200 --gpu-count 8"
echo ""
echo -e "${YELLOW}Configuration saved to .shadeform_config${NC}"