FROM node:24-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends redis-server curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY word-count-app/ ./word-count-app/
RUN sh word-count-app/fetch_books.sh && ls -l word-count-app/books

COPY start.sh ./
EXPOSE 9002

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD curl -fsS http://127.0.0.1:9002/word-chart-app/api/books || exit 1

CMD ["sh", "/app/start.sh"]
