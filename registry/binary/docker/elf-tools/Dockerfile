# Базовый образ Ubuntu
FROM ubuntu:22.04

# Устанавливаем инструменты для анализа ELF
RUN apt-get update && apt-get install -y \
    binutils \
    file \
    gdb \
    ltrace \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /workspace

# По умолчанию запускаем bash
CMD ["bash"]
