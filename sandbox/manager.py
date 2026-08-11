"""
Sandbox Manager - Безопасное выполнение в Docker-контейнерах.
Zero-Trust: изоляция, read-only, без сети, монтаж одного файла.

Sandbox Manager - Safe execution in Docker containers.
Zero-Trust: isolation, read-only, no network, single-file mount.
"""

import docker
import os
import shutil
import tempfile
from audit import AuditLogger

# Разрешённые директории (env CSR_ALLOWED_ROOTS, разделитель ":", дефолт ~/analysis)
# Allowed directories for analysis (env CSR_ALLOWED_ROOTS, ":" separated)
ALLOWED_ROOTS = [
    os.path.realpath(os.path.expanduser(p))
    for p in os.environ.get("CSR_ALLOWED_ROOTS", "~/analysis").split(":")
    if p.strip()
]

DEFAULT_TIMEOUT = 60  # секунд / seconds


class SandboxError(Exception):
    """Ошибка песочницы / Sandbox error"""


class SandboxManager:
    def __init__(self, skill_config: dict):
        self.config = skill_config.get("sandbox", {})
        self.workflow = skill_config.get("workflow", [])
        self.skill_name = skill_config.get("name", "unknown")
        self.skill_id = skill_config.get("skill_id", "unknown")
        self.timeout = int(self.config.get("timeout", DEFAULT_TIMEOUT))

        try:
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException as e:
            raise SandboxError(f"Docker не доступен / Docker not available: {e}")

        self.audit = AuditLogger()

    def _resolve_target(self, target_file: str) -> str:
        """Разрешает путь (realpath против symlink) и проверяет белый список.
        Resolves path (realpath vs symlinks) and checks the allowlist."""
        real = os.path.realpath(os.path.expanduser(target_file))
        for root in ALLOWED_ROOTS:
            if real == root or real.startswith(root + os.sep):
                return real
        raise SandboxError(
            f"Путь вне разрешённых директорий / Path outside allowed roots: {real}. "
            f"Разрешено / Allowed: {', '.join(ALLOWED_ROOTS)}"
        )

    def _build_commands(self, target_name: str) -> str:
        """Только декларативный workflow. Никаких внешних аргументов.
        Declarative workflow only. No external arguments."""
        commands = []
        for step in self.workflow:
            cmd = step.get("action", "")
            cmd = cmd.replace("<target>", f"/workspace/{target_name}")
            cmd = cmd.replace("<file>", f"/workspace/{target_name}")
            if cmd:
                commands.append(cmd)
        return " && ".join(commands)

    def execute_in_sandbox(self, target_file: str) -> str:
        """Запускает workflow в изолированном контейнере с одним файлом.
        Runs the workflow in an isolated container with a single file."""
        real_target = self._resolve_target(target_file)
        target_name = os.path.basename(real_target)

        image_name = self.config.get("image", "alpine:latest")
        try:
            self.client.images.get(image_name)
        except docker.errors.ImageNotFound:
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error_image_missing")
            raise SandboxError(f"Docker образ не найден / Image not found: '{image_name}'")

        full_script = self._build_commands(target_name)
        if not full_script:
            raise SandboxError("Нет команд в workflow / No commands in workflow")

        # Только один файл во временной папке / Single file in a temp dir
        tmp_dir = tempfile.mkdtemp(prefix="csr_")
        try:
            dst = os.path.join(tmp_dir, target_name)
            shutil.copy2(real_target, dst)
            os.chmod(tmp_dir, 0o755)  # доступно для nobody в контейнере / readable by nobody
            os.chmod(dst, 0o644)

            print(f"🔒 Запуск в изолированной среде / Isolated run: {image_name}")
            container = self.client.containers.create(
                image_name,
                command=["sh", "-c", full_script],
                volumes={tmp_dir: {"bind": "/workspace", "mode": "ro"}},
                tmpfs={"/tmp": "size=64m"},
                mem_limit="1g",
                pids_limit=64,
                cpu_period=100000,
                cpu_quota=50000,
                network_mode="none",
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                user="65534:65534",
                read_only=True,
            )
            try:
                container.start()
                container.wait(timeout=self.timeout)
                output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            except Exception:
                self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error_timeout")
                raise SandboxError(f"Таймаут / Timeout: {self.timeout}s")
            finally:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "success")
            return output if output.strip() else "✅ Анализ завершен / Analysis completed"

        except SandboxError:
            raise
        except docker.errors.APIError as e:
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error")
            return f"⚠️ Ошибка Docker / Docker error: {type(e).__name__}"
        except Exception:
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error")
            return "⚠️ Непредвиденная ошибка / Unexpected error"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
