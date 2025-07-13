# Указываем образ Python 3.13 с поддержкой Rust
FROM python:3.13-slim

# Устанавливаем зависимости для сборки Rust-библиотек
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    git \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y

# Устанавливаем переменные окружения для Rust
ENV PATH="/root/.cargo/bin:$PATH"

# Создаём рабочую директорию
WORKDIR /app

# Копируем проект
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Устанавливаем переменные окружения (можно заменить или убрать в Render)
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "bot.py"]
