FROM python:3.11-slim

WORKDIR /app

# 타임존 한국 시간(KST) 고정
ENV TZ=Asia/Seoul

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
