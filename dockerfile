FROM python:3.11-slim

# Pre-install data science and math tools inside the sandbox image
RUN pip install --no-cache-dir pandas numpy matplotlib seaborn sympy scipy

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set container working directory to project root
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project folders
COPY . .

# Ensure Python looks in /app and /app/app for imports
ENV PYTHONPATH=/app:/app/app

# Pre-create data and workspace folders & grant non-root permissions
RUN mkdir -p /app/data /app/nova_workspace /app/app/tools/nova_workspace && \
    useradd -m novauser && \
    chown -R novauser:novauser /app

USER novauser

# Run main.py using its relative path inside app/
CMD ["python", "app/main.py"]