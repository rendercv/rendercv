# Use the official Python image as a base
FROM python:3.11-slim

# Install system dependencies and full texlive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-full \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir rendercv==1.17

# Copy the application code
COPY app/ ./app/

# Create necessary directories with proper permissions
RUN mkdir -p /app/rendercv_output && \
    chmod 777 /app/rendercv_output

# Set environment variables for rendercv
ENV RENDERCV_OUTPUT_DIR=/app/rendercv_output

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
