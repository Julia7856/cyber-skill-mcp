# 🛡️ Cyber Skill Router

**Sandbox-First MCP Server для безопасного реверс-инжиниринга**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Что это?

Cyber Skill Router — это MCP-сервер, который позволяет ИИ-агентам (Claude, Cursor, Windsurf) безопасно выполнять задачи реверс-инжиниринга в **полностью изолированных Docker-контейнерах**.

### Ключевые особенности

- 🔒 **Sandbox-First**: Каждое действие выполняется в изолированном контейнере без доступа к сети
- ️ **Zero-Trust**: Read-only файловая система, ограничение памяти, запрет повышения привилегий
- 📦 **Декларативные навыки**: Добавляйте новые навыки через YAML-файлы без изменения кода
- 🤖 **MCP-совместимость**: Работает с Claude Desktop, Cursor, Windsurf
- ⚡ **CLI-интерфейс**: Запуск анализа одной командой без ИИ-агента
- 📜 **Audit Log**: Автоматический журнал всех действий для юридической чистоты
- ⚖️ **Этика по умолчанию**: White-hat only, образовательные цели и легальный аудит

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
git clone https://github.com/Julia7856/cyber-skill-mcp.git
cd cyber-skill-mcp
pip install -e .
```

### 2. Сборка Docker-образа

```bash
docker build -t cyber-skill/apk-tools:latest docker/apk-tools/
```

### 3. Настройка MCP-клиента

Добавьте в конфигурацию вашего клиента:

```json
{
  "mcpServers": {
    "cyber-skill-router": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/cyber-skill-mcp"
    }
  }
}
```

## ⚡ Использование через CLI

Вы можете запускать анализ прямо из командной строки, без ИИ-агента:

```bash
# Показать все доступные навыки
python cli.py list

# Запустить анализ файла
python cli.py analyze app.apk --skill apk_reverse_001
```

## 📜 Audit Log (Журнал аудита)

Каждый анализ автоматически записывается в файл `audit.log` в корне проекта.

**Что записывается:**
- ⏰ Время анализа
- 🔧 Использованный навык
- 🔐 SHA-256 хэш файла (цифровой отпечаток)
- ✅ Результат (success / error)

**Что НЕ записывается:**
- ❌ Содержимое анализируемых файлов
- ❌ Результаты анализа

Это обеспечивает полную прозрачность действий при сохранении конфиденциальности данных.

## 📂 Структура проекта
## 📦 Доступные навыки

### 📱 Мобильные приложения
* **`apk_reverse_001`** — Android APK Reverse Engineering
  * Извлечение `AndroidManifest.xml`
  * Декомпиляция Java/Kotlin кода
  * Поиск чувствительных строк, API-ключей и URL

### 💻 Бинарные файлы (Reverse Engineering)
* **`elf_reverse_001`** — Linux ELF Binary Analysis
  * Анализ структуры ELF-заголовков
  * Проверка динамических библиотек (ldd)
  * Дизассемблирование и поиск строк
* **`pe_analysis_001`** — Windows PE File Analysis
  * Парсинг PE-заголовков
  * Поиск подозрительных импортов (VirtualAlloc, CreateRemoteThread)
  * Извлечение строк и скрытых URL

### 🌐 Веб-безопасность
* **`js_deobfuscate_001`** — JavaScript Deobfuscation
  * Анализ обфусцированного JS-кода
  * Поиск подозрительных паттернов (`eval`, `Function`, `unescape`)
  * Извлечение скрытых ссылок и токенов

## ️ Добавление нового навыка

1. Создайте YAML-файл в `registry/`:

```yaml
skill_id: "my_skill_001"
name: "My Custom Skill"
description: "Описание навыка"
category: "custom"

sandbox:
  image: "my-docker-image:latest"

workflow:
  - step: 1
    action: "echo 'War 1' && my-command <target>"
```

2. Создайте Dockerfile в `docker/my-tools/`
3. Соберите образ: `docker build -t my-docker-image:latest docker/my-tools/`
4. Перезапустите MCP-сервер

## ⚠️ Этический дисклеймер

Этот инструмент предназначен **исключительно** для:
- ✅ Образовательных целей
- ✅ Анализа собственных файлов
- ✅ CTF-задач и исследований безопасности
- ✅ Легального аудита с явного согласия владельца

**Запрещено использовать для:**
- ❌ Несанкционированного доступа к чужим системам
- ❌ Вредоносных действий
- ❌ Нарушения законов

## 📄 Лицензия

MIT License - см. файл LICENSE

---

**Сделано с ❤️ для безопасного и этичного реверс-инжиниринга**
