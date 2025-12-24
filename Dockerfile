FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/ast-grep/ast-grep/releases/download/0.27.3/ast-grep-v0.27.3-x86_64-unknown-linux-gnu.tar.gz | \
    tar xz && \
    mv ast-grep-v0.27.3-x86_64-unknown-linux-gnu/ast-grep /usr/local/bin/ && \
    chmod +x /usr/local/bin/ast-grep && \
    rm -rf ast-grep-v0.27.3-x86_64-unknown-linux-gnu

RUN npm install -g @mermaid-js/mermaid-cli

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8080

CMD ["python", "-m", "app.main"]
