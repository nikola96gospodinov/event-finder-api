FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir .

RUN useradd -m -u 1000 appuser

RUN playwright install chromium --with-deps

RUN mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/ms-playwright /home/appuser/.cache/ && \
    chown -R appuser:appuser /home/appuser/.cache/ms-playwright

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x startup.sh && \
    chown appuser:appuser startup.sh && \
    chown -R appuser:appuser /etc/supervisor/conf.d/

USER appuser

EXPOSE 8080

CMD ["./startup.sh"]