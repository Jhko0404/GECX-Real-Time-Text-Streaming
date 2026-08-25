# Multi-Stage Build for GECX Text Streaming Cockpit BFF

# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# Stage 2: Python BFF Runtime
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bff/ ./bff/
COPY --from=frontend-builder /app/web/dist ./web/dist

EXPOSE 8080

CMD ["uvicorn", "bff.main:app", "--host", "0.0.0.0", "--port", "8080"]
