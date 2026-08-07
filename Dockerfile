# Python 3.11.9 - webhook rejimida ishlaydigan Telegram bot
FROM python:3.11.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# requirements avval kopiyalanadi - Docker cache uchun
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodi
COPY . .

EXPOSE 10000

CMD ["python", "main.py"]
