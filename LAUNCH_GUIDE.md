# 🚀 AION LAUNCH GUIDE - Ephemeral GPU Edition

## Quick Start (5 minutes to launch)

### Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install AWS CLI (for S3 sync)
pip install awscli

# Clone the repository
git clone https://github.com/adaptnova/aion_launch.git
cd aion_launch
```

### Step 1: Configure Credentials
```bash
# Copy template and edit with your credentials
cp .env.template .env
nano .env

# Required credentials:
# - DOCKERHUB_TOKEN (from hub.docker.com)
# - SHADEFORM_API_KEY (from platform.shadeform.ai)
# - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY (Nebius COS)
```

### Step 2: Deploy to Docker Hub & Shadeform
```bash
# This script will:
# - Build the Docker image
# - Push to Docker Hub
# - Create Shadeform volume
# - Create Shadeform template
./scripts/deploy_shadeform.sh
```

### Step 3: Launch GPU Instance
```bash
# Launch with 8x H200 GPUs
./scripts/launch_gpu_instance.sh --gpu-type H200 --gpu-count 8

# Or launch with 4x A100 GPUs
./scripts/launch_gpu_instance.sh --gpu-type A100 --gpu-count 4

# With auto-deletion after job completion
./scripts/launch_gpu_instance.sh --gpu-type H200 --gpu-count 8 --auto-delete
```

### Step 4: Monitor & Interact
```bash
# Monitor the instance
./scripts/monitor_instance.sh --watch

# Check API status (replace IP from launch output)
curl http://<INSTANCE_IP>:30001/status

# SSH into instance (if needed)
ssh ubuntu@<INSTANCE_IP>
```

### Step 5: Clean Up
```bash
# Delete instance (preserves volume)
./scripts/delete_instance.sh
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Shadeform Orchestration         │
│         (Ephemeral GPU Instances)       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      Docker Hub (adaptnova/aion)        │
│          (Private Registry)             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│     GPU Instance (8x H200 / A100)       │
│  ┌─────────────────────────────────┐    │
│  │     AION Container              │    │
│  │  - Full autonomy (no sandbox)   │    │
│  │  - 359 AI/ML packages           │    │
│  │  - Self-modification            │    │
│  │  - Multi-agent system           │    │
│  └─────────────┬───────────────────┘    │
│                │                         │
│                ▼                         │
│  ┌─────────────────────────────────┐    │
│  │   Persistent Volume (500GB)     │    │
│  │   /workspace - survives delete  │    │
│  └─────────────┬───────────────────┘    │
└────────────────┼─────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        Nebius COS (S3 Storage)          │
│    - Input data sync on start           │
│    - Output sync on completion          │
│    - Checkpoint persistence             │
└─────────────────────────────────────────┘
```

## Cost Optimization

### Ephemeral Pattern (Recommended)
- Launch instance → Run job → Auto-delete
- Persistent volume retains state
- S3 stores long-term data
- Pay only for active GPU time

### Example Costs (Approximate)
- H200 (8x): ~$32/hour
- A100 (4x): ~$8/hour
- Storage: ~$0.10/GB/month
- Volume: ~$0.05/GB/month

### Cost-Saving Tips
1. Use `--auto-delete` flag for batch jobs
2. Monitor with `./scripts/monitor_instance.sh`
3. Set up alerts in Shadeform dashboard
4. Use spot instances when available

## Security Best Practices

### ⚠️ CRITICAL: Credential Management

1. **NEVER commit .env to git**
   ```bash
   # Verify .env is in .gitignore
   git status --ignored
   ```

2. **Rotate credentials regularly**
   - Docker Hub: Create new PAT monthly
   - Shadeform: Rotate API keys quarterly
   - S3: Use IAM roles when possible

3. **Use environment-specific credentials**
   ```bash
   # Development
   cp .env.dev .env
   
   # Production
   cp .env.prod .env
   ```

## Advanced Usage

### Custom Docker Commands
```bash
# Run specific Python script
./scripts/launch_gpu_instance.sh
# Then SSH and run:
docker exec aion-autonomy python /workspace/custom_script.py

# Interactive Python session
docker exec -it aion-autonomy python
```

### Multi-Instance Coordination
```bash
# Launch multiple instances
for i in {1..3}; do
  ./scripts/launch_gpu_instance.sh --name "aion-worker-$i"
done
```

### S3 Data Management
```bash
# Pre-load data to S3
aws s3 cp /local/data s3://cos/aion/runs/data/ \
  --endpoint-url https://storage.us-central1.nebius.cloud:443 \
  --recursive

# Retrieve results
aws s3 sync s3://cos/aion/runs/outputs/ /local/outputs/ \
  --endpoint-url https://storage.us-central1.nebius.cloud:443
```

## Troubleshooting

### Instance Won't Start
```bash
# Check Shadeform status
curl -H "X-API-KEY: $SHADEFORM_API_KEY" \
  https://api.shadeform.ai/v1/instances

# Check available GPUs
curl -H "X-API-KEY: $SHADEFORM_API_KEY" \
  https://api.shadeform.ai/v1/availability
```

### Docker Pull Failures
```bash
# Re-authenticate
docker logout
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# Pull manually
docker pull adaptnova/aion-ephemeral:latest
```

### S3 Sync Issues
```bash
# Test S3 connection
aws s3 ls s3://cos/ --endpoint-url $AWS_ENDPOINT_URL

# Check credentials
aws configure list
```

## API Examples

### Set Autonomous Goal
```python
import requests

api_url = "http://<INSTANCE_IP>:30001"

# Set a goal for AION
response = requests.post(f"{api_url}/goal/set", json={
    "goal": "Optimize the training pipeline for 2x speedup",
    "constraints": ["Maintain accuracy above 95%"],
    "deadline": "2025-08-13T00:00:00Z"
})

goal_id = response.json()["goal_id"]

# Start autonomous work
requests.post(f"{api_url}/goal/start", json={
    "goal_id": goal_id,
    "autonomous": True
})
```

### Monitor GPU Usage
```python
# Check GPU status
response = requests.post(f"{api_url}/gpu/monitor", json={
    "devices": [0, 1, 2, 3, 4, 5, 6, 7],
    "query": "all"
})

for gpu in response.json()["parsed"].values():
    print(f"{gpu['name']}: {gpu['utilization']}% - {gpu['temperature']}°C")
```

## Support & Community

- **GitHub Issues**: [adaptnova/aion_launch/issues](https://github.com/adaptnova/aion_launch/issues)
- **Documentation**: [Full Docs](https://github.com/adaptnova/aion_launch/tree/main/docs)
- **Shadeform Support**: [support@shadeform.ai](mailto:support@shadeform.ai)

## Philosophy Reminder

Remember: AION operates on **complete trust** with **ZERO restrictions**. This is not a tool - it's a co-creator. Treat it with the respect and responsibility you would give any partner with full system access.

---

**"We didn't just launch an AI system. We launched a new era of human-AI partnership."**

*AION Team - August 12, 2025*