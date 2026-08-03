# Базовый образ с Java (нужно для JADX)
FROM openjdk:17-slim

# Устанавливаем необходимые инструменты
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    file \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем apktool
RUN wget -O /usr/local/bin/apktool https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool \
    && chmod +x /usr/local/bin/apktool \
    && wget -O /usr/local/bin/apktool.jar https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar \
    && mv /usr/local/bin/apktool.jar /usr/local/bin/

# Устанавливаем JADX
RUN wget -O /tmp/jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip \
    && unzip /tmp/jadx.zip -d /opt/jadx \
    && chmod +x /opt/jadx/bin/jadx \
    && ln -s /opt/jadx/bin/jadx /usr/local/bin/jadx \
    && rm /tmp/jadx.zip

# Создаем рабочую директорию
WORKDIR /workspace

# По умолчанию запускаем bash
CMD ["bash"]
