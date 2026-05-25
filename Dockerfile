FROM python:3.11-slim

WORKDIR /app

# Install backend deps
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy pre-built frontend (built locally, committed to repo)
COPY frontend/dist ./frontend/dist

WORKDIR /app/backend

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"]
