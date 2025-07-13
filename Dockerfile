# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем rust и другие зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libffi-dev \
    build-essential \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем pip и обновляем
RUN python -m pip install --upgrade pip

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости, принудительно отключая сборку из исходников
ENV PIP_NO_BUILD_ISOLATION=1
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt

# Запуск приложения
CMD ["python", "main.py"]
