# Базовый образ Python
FROM python:3.10-slim

# Устанавливаем системные инструменты
RUN apt-get update && apt-get install -y \
    file \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-библиотеки для анализа PE
RUN pip install --no-cache-dir pefile

# Создаем рабочую директорию
WORKDIR /workspace

# По умолчанию запускаем bash
CMD ["bash"]
