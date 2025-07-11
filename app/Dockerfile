FROM python:3.11-slim

# Set work directory
WORKDIR /workspace

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install OS packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
