FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy data into image (so it's available in K8s)
COPY data/ /app/data/

# Expose port for Streamlit
EXPOSE 8501

# Default command
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]