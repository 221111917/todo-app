FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Folder untuk DB dan uploads
RUN mkdir -p /data /uploads

EXPOSE 5000

# Healthcheck untuk Kubernetes (pastikan app ready)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:5000/ || exit 1

CMD ["python", "app.py"]