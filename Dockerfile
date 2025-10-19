FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
RUN pip install --no-cache-dir \
    numpy \
    matplotlib \
    ezdxf

# Создаём папку для вывода (опционально — можно монтировать и её)
RUN mkdir -p output


CMD ["python", "calc-vpts.py"]
