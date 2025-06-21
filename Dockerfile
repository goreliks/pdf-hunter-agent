FROM python:3.12-slim

# Install system dependencies for PDF analysis tools and libmagic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 pdfanalyst && chown -R pdfanalyst:pdfanalyst /app
USER pdfanalyst

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command to run the static analysis agent
CMD ["python", "static_analysis_agent.py"]