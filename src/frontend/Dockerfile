FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY . .

CMD ["python", "-m", "http.server", "5500"]