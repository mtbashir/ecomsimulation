# Portability: the same image runs on Fly, Railway, a VPS or your laptop.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ECOMSIM_DB=/var/data/game.db

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /var/data
VOLUME ["/var/data"]

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/healthz')"

CMD ["gunicorn", "wsgi:app", "--workers", "1", "--threads", "8", \
     "--timeout", "120", "--bind", "0.0.0.0:8000"]
