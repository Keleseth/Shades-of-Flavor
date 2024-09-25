FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

RUN pip install gunicorn==20.1.0

COPY . .

CMD ["sh", "entrypoint.sh"]