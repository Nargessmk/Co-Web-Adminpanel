FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-build-isolation setuptools wheel && \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . .

RUN mkdir -p uploads/profile-images

EXPOSE ${PORT:-6200}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6200"]
