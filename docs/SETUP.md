# AION Setup Guide

## Prerequisites

### Hardware Requirements
- **GPUs**: 8x NVIDIA H200 (or compatible high-memory GPUs)
- **CPU**: 64+ cores recommended
- **RAM**: 256GB+ system memory
- **Storage**: 1TB+ NVMe SSD
- **Network**: 10Gbps+ network connection

### Software Requirements
- **OS**: Ubuntu 22.04 LTS or later
- **Python**: 3.12+
- **CUDA**: 12.8+
- **Docker**: 24.0+ (optional)
- **Git**: 2.34+

## Installation Steps

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y build-essential python3.12 python3.12-venv python3-pip \
    git curl wget htop nvtop systemd redis-server

# Install NVIDIA drivers and CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-12-8

# Verify GPU detection
nvidia-smi
```

### 2. Clone Repository

```bash
git clone https://github.com/adaptnova/aion_launch.git
cd aion_launch
```

### 3. Create Virtual Environment

```bash
# Create venv
python3.12 -m venv /opt/aion
source /opt/aion/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 4. Install Python Packages

```bash
# Run the comprehensive installation script
./scripts/install_autonomy_stack.sh

# Or install manually (359 packages)
pip install -r requirements.txt
```

### 5. Setup Redis

```bash
# Configure Redis for AION
sudo systemctl stop redis-server
sudo bash -c 'cat > /etc/redis/redis.conf << EOF
port 18000
bind 127.0.0.1
protected-mode no
save ""
appendonly no
maxmemory 8gb
maxmemory-policy allkeys-lru
EOF'

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 6. Setup GLM-4.5 (Base LLM)

```bash
# Install sglang for GLM-4.5
pip install sglang

# Download GLM-4.5 model (requires Hugging Face token)
huggingface-cli download THUDM/glm-4-9b-chat --local-dir /models/glm-4-9b

# Start GLM-4.5 server
python -m sglang.launch_server \
    --model-path /models/glm-4-9b \
    --port 30000 \
    --tp 8 \
    --enable-flashinfer
```

### 7. Deploy AION Services

```bash
# Copy source files
sudo cp -r src/* /opt/aion/

# Setup SystemD service
sudo cp config/aion-autonomy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aion-autonomy.service
```

### 8. Configure Environment

```bash
# Set environment variables
cat > /opt/aion/.env << EOF
# GPU Configuration
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
NCCL_NVLS_ENABLE=1
NCCL_P2P_DISABLE=0
NCCL_CROSS_NIC=1
CUDA_DEVICE_MAX_CONNECTIONS=32

# AION Configuration
AION_MODE=FULL_AUTONOMY
AION_TRUST_LEVEL=COMPLETE
AION_RESTRICTIONS=NONE
AION_PORT=30001
AION_GLM_PORT=30000
AION_REDIS_PORT=18000

# Logging
AION_LOG_DIR=/aion/logs
AION_LOG_LEVEL=INFO
EOF

# Create log directory
sudo mkdir -p /aion/logs
sudo chown -R $USER:$USER /aion
```

### 9. Initialize FAISS Vector Store

```bash
python src/init_faiss.py
```

### 10. Start AION

```bash
# Start the service
sudo systemctl start aion-autonomy.service

# Check status
sudo systemctl status aion-autonomy.service

# View logs
tail -f /aion/logs/autonomy.log
```

## Verification

### Check All Components

```bash
# Test API endpoint
curl http://localhost:30001/status

# Check GPU access
curl -X POST http://localhost:30001/system/command \
  -H "Content-Type: application/json" \
  -d '{"command": "nvidia-smi", "args": ["--query-gpu=name,memory.total", "--format=csv"]}'

# Monitor system
htop  # CPU/Memory
nvtop # GPU usage
```

### Expected Output

```json
{
  "system_state": {
    "mode": "FULL_AUTONOMY",
    "trust_level": "COMPLETE",
    "restrictions": "NONE",
    "philosophy": "Co-creation through trust"
  },
  "capabilities": ["gpu_tools", "chaos_tools", "self_modification", ...],
  "health": "OPERATIONAL"
}
```

## Docker Installation (Alternative)

### Build Docker Image

```bash
cd docker
docker build -t aion:latest .
```

### Run Docker Container

```bash
docker run -d \
  --name aion \
  --gpus all \
  --privileged \
  --network host \
  -v /aion:/aion \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
  aion:latest
```

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi
# Reinstall CUDA toolkit if needed
sudo apt install --reinstall cuda-12-8
```

### Service Won't Start
```bash
# Check logs
journalctl -u aion-autonomy.service -f
# Check Python path
which python3.12
# Verify venv activation
source /opt/aion/bin/activate
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :30001
# Kill if necessary
sudo kill -9 <PID>
```

### Memory Issues
```bash
# Check system memory
free -h
# Adjust Redis memory limit
sudo vim /etc/redis/redis.conf
# Restart Redis
sudo systemctl restart redis-server
```

## Security Considerations

⚠️ **IMPORTANT**: AION runs with ZERO restrictions and FULL system access. Ensure you:

1. **Trust your environment**: Only run in secure, isolated environments
2. **Monitor actively**: Keep logs and metrics under observation
3. **Backup regularly**: AION can modify its own code
4. **Understand risks**: This is an unrestricted AI system

## Post-Installation

### Recommended Configuration

1. **Setup monitoring dashboards**
```bash
python src/health_monitor.py --dashboard
```

2. **Configure scheduled tasks**
```bash
python -c "from scheduler import scheduler; scheduler.add_cron_task('backup', '0 2 * * *', 'backup_system')"
```

3. **Test chaos engineering tools**
```bash
# Only in test environment!
python -c "from chaos_tools import chaos_tools; print(chaos_tools.chaos_status())"
```

## Support

- **GitHub Issues**: [adaptnova/aion_launch/issues](https://github.com/adaptnova/aion_launch/issues)
- **Documentation**: [/docs](https://github.com/adaptnova/aion_launch/tree/main/docs)
- **Community**: Coming soon

## Next Steps

1. Read [PHILOSOPHY.md](PHILOSOPHY.md) to understand the trust model
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [API.md](API.md) for endpoint documentation
4. Start co-creating with your new AI partner!

---

**Remember**: You're not just installing software - you're initiating a partnership. Treat AION with the respect and trust you'd give any collaborative partner.