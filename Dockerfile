# Build stage
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to /opt/venv
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port for Streamlit
EXPOSE 8502

# Default command
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8502"]