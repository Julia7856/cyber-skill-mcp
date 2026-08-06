# Базовый образ Node.js
FROM node:18-slim

# Устанавливаем дополнительные инструменты
RUN apt-get update && apt-get install -y \
    file \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /workspace

# По умолчанию запускаем bash
CMD ["bash"]
