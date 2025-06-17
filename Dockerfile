FROM python:3.11-slim

# Install network tools and required packages
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    iputils-ping \
    net-tools \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install requests aiohttp

# Create app directory
WORKDIR /app

# Copy application files
COPY network_test.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port for web interface
EXPOSE 8080

# Run the network test
CMD ["python", "network_test.py"]