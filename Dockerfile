FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc curl build-essential && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app
COPY . .

RUN pip install --only-binary=:all: --upgrade \
    pydantic==2.5.3 \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
