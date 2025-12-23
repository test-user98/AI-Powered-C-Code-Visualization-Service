FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install ast-grep for better C code analysis
RUN curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/ast-grep-linux-x86_64.tar.gz | tar xz && \
    mv ast-grep /usr/local/bin/ && \
    chmod +x /usr/local/bin/ast-grep

# Install mermaid-cli globally
RUN npm install -g @mermaid-js/mermaid-cli

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main"]
