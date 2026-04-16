FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG XRAY_VERSION=v1.8.24
RUN curl -L -o /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip" \
    && unzip /tmp/xray.zip -d /tmp/xray \
    && install -m 755 /tmp/xray/xray /usr/local/bin/xray \
    && rm -rf /tmp/xray /tmp/xray.zip

COPY . .

CMD ["python", "main.py"]