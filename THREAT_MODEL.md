# 🛡️ Threat Model / Модель угроз

**Cyber Skill Router — honest security posture / честная модель безопасности**

> Honest security is better than marketing promises.
> Честная безопасность лучше маркетинговых обещаний.

## Scope / Область действия

This document describes what the project protects against, what it does NOT
protect against, and where the trust boundaries lie.
Документ описывает, от чего защищает проект, от чего НЕ защищает и где
проходят границы доверия.

## Trust boundaries / Границы доверия

| Component / Компонент | Trust / Доверие |
|---|---|
| `registry/*.yaml` (skills / навыки) | ✅ Trusted / доверенные (repo owner / владелец) |
| CLI user / пользователь CLI | ✅ Trusted human / доверенный человек |
| Host running Docker / хост с Docker | ✅ Trusted / доверенный |
| AI agent (MCP client) / ИИ-агент | ❌ Untrusted / недоверенный |
| Analyzed files / анализируемые файлы | ❌ Untrusted / недоверенные |
| Container output / вывод контейнера | ❌ Untrusted data / недоверенные данные |

## Threats & mitigations / Угрозы и защита

### 1. Prompt-injection from a malicious file / из вредоносного файла
**Attack / Атака:** file content manipulates the AI agent into misusing tools /
содержимое файла заставляет агента злоупотребить инструментом.
**Mitigation / Защита:** input contract `target_file` only; allowlist of roots +
`realpath()`; single-file mount; sanitized output with `UNTRUSTED OUTPUT` markers /
контракт только `target_file`; белый список папок + `realpath()`; монтаж одного файла;
санация вывода с маркерами.

### 2. Arbitrary command execution / произвольные команды
**Attack / Атака:** command injection via tool arguments / инъекция через аргументы.
**Mitigation / Защита:** declarative workflow from trusted YAML; `extra_args` removed
from the MCP contract / декларативный workflow; `extra_args` удалён из контракта.

### 3. Arbitrary host file read / чтение файлов хоста
**Attack / Атака:** agent asks to analyze `/etc/shadow`, `~/.ssh/*` /
агент просит «анализ» `/etc/shadow`, `~/.ssh/*`.
**Mitigation / Защита:** `CSR_ALLOWED_ROOTS` (default `~/analysis`), `realpath()`
vs symlinks / белый список + защита от symlink.

### 4. Container escape / побег из контейнера
**Mitigation / Защита:** `read_only`, `cap_drop=ALL`, `no-new-privileges`,
`network_mode=none`, `user=65534`, local images only (no auto-pull) /
read-only, сброшенные capabilities, без сети, nobody, образы только локальные.

### 5. Host DoS / DoS против хоста
**Mitigation / Защита:** `mem_limit=1g`, `pids_limit=64`, CPU quota 50%,
timeout 60 s (per-skill configurable) / лимиты памяти, PID, CPU и таймаут.

### 6. Supply chain / цепочка поставок
**Mitigation / Защита:** no automatic image pulls; YAML via `safe_load` /
без автоскачивания образов; YAML через `safe_load`.
**Recommendation / Рекомендация:** pin images by digest / пиннить образы по digest
(`image@sha256:...`).

## What we do NOT claim / Что мы НЕ утверждаем

- ❌ `audit.log` is not tamper-proof — best-effort transparency record, not a
  cryptographic guarantee / журнал не защищён от подмены: best-effort запись,
  не криптографическая гарантия.
- ❌ `registry/` is a trust boundary: who can edit a skill YAML can run commands
  in the container (by design) / кто правит YAML навыка, тот выполняет команды
  в контейнере (по дизайну).
- ❌ The Docker socket gives the server full Docker control: run only on a
  trusted host / Docker-сокет = полный контроль над Docker: только доверенный хост.
- ❌ Output sanitization reduces but does not eliminate prompt-injection risk /
  санация снижает, но не устраняет риск prompt-injection полностью.

## Responsible use / Ответственное использование

White-hat only: own files, CTF, research, authorized audit /
Только white-hat: собственные файлы, CTF, исследования, авторизованный аудит.

## Reporting / Сообщение об уязвимостях

GitHub → Security → Report a vulnerability (private) / приватно.
