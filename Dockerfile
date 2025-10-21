FROM python:3.12-slim

WORKDIR /app
ENV TZ=Asia/Jakarta

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY saham-alert.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "saham-alert.py"]

