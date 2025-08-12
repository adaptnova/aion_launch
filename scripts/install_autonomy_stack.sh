#!/bin/bash
# Install complete autonomy stack for AION

echo "🚀 Installing AION Complete Autonomy Stack..."
source /opt/aion/bin/activate

# Core Data Science & ML
echo "📊 Installing data science tools..."
pip install pandas numpy scipy matplotlib seaborn plotly scikit-learn xgboost lightgbm

# Deep Learning Frameworks (CPU versions for now, GPU versions can be added later)
echo "🧠 Installing deep learning frameworks..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install tensorflow keras

# Computer Vision
echo "👁️ Installing vision capabilities..."
pip install opencv-python opencv-contrib-python pillow imageio scikit-image

# Audio Processing
echo "🔊 Installing audio capabilities..."
pip install speechrecognition pyttsx3 pyaudio soundfile librosa pydub

# Natural Language Processing
echo "💬 Installing NLP tools..."
pip install transformers nltk spacy textblob gensim sentence-transformers

# Web Scraping & Automation
echo "🌐 Installing web automation tools..."
pip install beautifulsoup4 selenium scrapy requests-html pyppeteer lxml

# Database Clients
echo "🗄️ Installing database clients..."
pip install pymongo psycopg2-binary mysql-connector-python redis-py neo4j cassandra-driver influxdb-client

# LLM & AI APIs
echo "🤖 Installing LLM integrations..."
pip install openai anthropic langchain langchain-community chromadb pinecone-client weaviate-client

# Message Queues & Async
echo "📨 Installing message queue clients..."
pip install celery pika aiokafka aioredis

# Monitoring & Observability
echo "📈 Installing monitoring tools..."
pip install prometheus-client grafana-api datadog statsd psutil py-cpuinfo

# Development Tools
echo "🛠️ Installing development tools..."
pip install black autopep8 pylint pytest ipython jupyter rich typer click

# Workflow Orchestration
echo "⚙️ Installing workflow tools..."
pip install prefect dagster apache-airflow schedule APScheduler

# Additional Utilities
echo "🔧 Installing additional utilities..."
pip install python-dotenv pyyaml toml httpx aiohttp websockets watchdog tenacity retrying backoff

echo "✅ AION Autonomy Stack Installation Complete!"
echo "📦 Total packages installed: $(pip list | wc -l)"