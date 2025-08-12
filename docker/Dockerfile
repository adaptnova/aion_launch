# AION Ultimate Autonomy Docker Image
# Full trust, no restrictions, complete hardware access
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

LABEL maintainer="AION Team"
LABEL description="AION - Fully Autonomous AI Co-Creator with 8x H200 GPU Support"
LABEL version="1.0.0"

# Environment setup
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
ENV NCCL_NVLS_ENABLE=1
ENV NCCL_P2P_DISABLE=0
ENV NCCL_CROSS_NIC=1
ENV CUDA_DEVICE_MAX_CONNECTIONS=32

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    build-essential \
    git \
    curl \
    wget \
    htop \
    nvtop \
    redis-server \
    systemd \
    sudo \
    vim \
    stress-ng \
    iproute2 \
    bpftrace \
    linux-tools-generic \
    && rm -rf /var/lib/apt/lists/*

# Create AION directory structure
RUN mkdir -p /opt/aion /aion/logs /aion/memory /aion/knowledge

# Set up Python virtual environment
RUN python3.12 -m venv /opt/aion
ENV PATH="/opt/aion/bin:$PATH"

# Upgrade pip
RUN /opt/aion/bin/pip install --upgrade pip setuptools wheel

# Copy requirements and install Python packages
COPY requirements.txt /tmp/
RUN /opt/aion/bin/pip install -r /tmp/requirements.txt

# Install additional AI/ML packages (359 total)
RUN /opt/aion/bin/pip install \
    torch torchvision torchaudio \
    tensorflow \
    jax jaxlib \
    transformers \
    langchain langchain-community \
    openai anthropic \
    scikit-learn xgboost lightgbm \
    pandas numpy scipy \
    matplotlib seaborn plotly \
    opencv-python-headless \
    faiss-cpu \
    redis \
    fastapi uvicorn \
    schedule \
    psutil \
    pytest \
    black ruff

# Copy AION source code
COPY src/ /opt/aion/
COPY scripts/ /opt/aion/scripts/
COPY config/ /opt/aion/config/

# Set up Redis configuration
RUN echo "port 18000\n\
bind 127.0.0.1\n\
protected-mode no\n\
save \"\"\n\
appendonly no\n\
maxmemory 8gb\n\
maxmemory-policy allkeys-lru" > /etc/redis/redis.conf

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Redis\n\
redis-server /etc/redis/redis.conf &\n\
\n\
# Wait for Redis\n\
sleep 2\n\
\n\
# Start AION\n\
cd /opt/aion\n\
/opt/aion/bin/python /opt/aion/full_autonomy_toolbelt.py\n\
' > /opt/aion/start.sh && chmod +x /opt/aion/start.sh

# Expose ports
EXPOSE 30001 18000

# Volume mounts for persistence
VOLUME ["/aion/logs", "/aion/memory", "/aion/knowledge"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:30001/health || exit 1

# Set working directory
WORKDIR /opt/aion

# Entry point - UNRESTRICTED AUTONOMY
ENTRYPOINT ["/opt/aion/start.sh"]