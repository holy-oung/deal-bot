FROM python:3.11-slim

WORKDIR /app

# 타임존 한국 시간(KST) 고정
ENV TZ=Asia/Seoul

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Hugging Face Spaces UID 1000 및 파일 쓰기 권한 부여
RUN useradd -m -u 1000 user && \
    chown -R user:user /app && \
    chmod -R 777 /app

USER user

EXPOSE 7860

CMD ["python", "main.py"]
