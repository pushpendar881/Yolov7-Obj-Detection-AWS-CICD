FROM python:3.8-slim
RUN apt update -y && apt install awscli -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "app.py"]
