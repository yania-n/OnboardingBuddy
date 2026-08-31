# Multi-stage build: Stage 1 builds React frontend, Stage 2 packages Python backend

# Stage 1: Build the React frontend with Vite
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python container
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend
ENV PORT=8080

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Copy compiled React frontend assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose Cloud Run default port
EXPOSE 8080

# Start FastAPI server
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

