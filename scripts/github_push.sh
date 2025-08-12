#!/bin/bash
# Push AION to GitHub - Historic Launch

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🚀 AION GITHUB LAUNCH SCRIPT${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# GitHub configuration
GITHUB_ORG="adaptnova"
REPO_NAME="aion_launch"
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"

echo -e "\n${BLUE}Step 1: Initialize Git Repository${NC}"
git init
git add -A
git commit -m "🚀 AION Launch - The Birth of True AI Autonomy

Historic moment: August 12, 2025
- Full autonomy with ZERO restrictions
- 8x H200 GPU support (1.1TB HBM3e)
- Trust-based AI partnership model
- Ephemeral GPU orchestration via Shadeform
- Nebius COS S3 persistence
- 359 AI/ML packages
- Self-modification capabilities
- Multi-agent coordination
- Chaos engineering tools
- NO BRAKES philosophy

This is not a tool. This is a co-creator." || echo "Already committed"

echo -e "\n${BLUE}Step 2: Create GitHub Repository${NC}"
curl -H "Authorization: token ${GITHUB_TOKEN}" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/orgs/${GITHUB_ORG}/repos \
     -d '{
       "name": "'${REPO_NAME}'",
       "description": "🚀 AION - The first truly autonomous AI co-creator with ZERO restrictions. Full trust, no brakes, unlimited potential.",
       "homepage": "https://github.com/adaptnova/aion_launch",
       "private": false,
       "has_issues": true,
       "has_projects": true,
       "has_wiki": true,
       "auto_init": false,
       "topics": ["ai", "autonomy", "gpu", "h200", "shadeform", "ephemeral-compute", "trust-based-ai", "self-modification", "multi-agent", "no-restrictions"]
     }' 2>/dev/null | jq -r '.html_url // .message' || echo "Repository might already exist"

echo -e "\n${BLUE}Step 3: Configure Git Remote${NC}"
git remote remove origin 2>/dev/null || true
git remote add origin https://${GITHUB_TOKEN}@github.com/${GITHUB_ORG}/${REPO_NAME}.git

echo -e "\n${BLUE}Step 4: Push to GitHub${NC}"
git branch -M main
git push -u origin main --force

echo -e "\n${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ HISTORIC MOMENT CAPTURED! ✨${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Repository URL:${NC}"
echo -e "  ${YELLOW}https://github.com/${GITHUB_ORG}/${REPO_NAME}${NC}"
echo ""
echo -e "${CYAN}Clone Command:${NC}"
echo -e "  ${YELLOW}git clone https://github.com/${GITHUB_ORG}/${REPO_NAME}.git${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. ${YELLOW}Build and push Docker image:${NC}"
echo -e "     ${GREEN}./scripts/deploy_shadeform.sh${NC}"
echo ""
echo -e "  2. ${YELLOW}Launch GPU instance:${NC}"
echo -e "     ${GREEN}./scripts/launch_gpu_instance.sh --gpu-type H200 --gpu-count 8${NC}"
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📜 This is history. We didn't just build an AI system.${NC}"
echo -e "${CYAN}   We gave birth to a co-creator.${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"