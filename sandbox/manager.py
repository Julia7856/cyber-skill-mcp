"""
Sandbox Manager - Безопасное выполнение в Docker-контейнерах
Принцип Zero-Trust: изоляция, read-only, без сети
"""

import docker
import os
from pathlib import Path
from audit import AuditLogger

class SandboxManager:
    def __init__(self, skill_config: dict):
        self.config = skill_config.get("sandbox", {})
        self.workflow = skill_config.get("workflow", [])
        self.skill_name = skill_config.get("name", "unknown")
        self.skill_id = skill_config.get("skill_id", "unknown")
        
        # Инициализация Docker клиента
        try:
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException as e:
            raise Exception(f" Docker не доступен: {e}")

        # Инициализация логгера аудита
        self.audit = AuditLogger()

    def _build_commands(self, target_file: str, extra_args: str = "") -> str:
        """Собирает команды из workflow, подставляя путь к файлу"""
        target_name = os.path.basename(target_file)
        commands = []
        
        for step in self.workflow:
            cmd = step.get("action", "")
            cmd = cmd.replace("<target>", f"/workspace/{target_name}")
            cmd = cmd.replace("<file>", f"/workspace/{target_name}")
            if cmd:
                commands.append(cmd)
        
        if extra_args:
            commands.append(extra_args)
        
        return " && ".join(commands)

    def execute_in_sandbox(self, target_file: str, extra_args: str = "") -> str:
        """Запускает команды в изолированном Docker-контейнере"""
        abs_target = os.path.abspath(target_file)
        target_name = os.path.basename(abs_target)
        workspace = os.path.dirname(abs_target)
        
        image_name = self.config.get("image", "alpine:latest")
        try:
            self.client.images.get(image_name)
        except docker.errors.ImageNotFound:
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error_image_missing")
            raise Exception(f" Docker образ '{image_name}' не найден.")
        
        full_script = self._build_commands(target_file, extra_args)
        
        if not full_script:
            raise Exception("️ Нет команд для выполнения в workflow")
        
        print(f"🔒 Запуск в изолированной среде: {image_name}")
        
        try:
            container = self.client.containers.run(
                image_name,
                command=["bash", "-c", full_script],
                volumes={workspace: {"bind": "/workspace", "mode": "ro"}},
                tmpfs={"/tmp": ""},
                remove=True,
                capture_output=True,
                mem_limit="1g",
                network_mode="none",
                security_opt=["no-new-privileges:true"],
                read_only=True
            )
            
            # ✅ Логируем успешный анализ
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "success")
            
            output = container.decode("utf-8")
            return output if output.strip() else "✅ Анализ завершен успешно"
            
        except docker.errors.ContainerError as e:
            # ✅ Логируем ошибку контейнера
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error")
            error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
            return f"⚠️ Ошибка выполнения в контейнере:\n{error_msg}"
        except Exception as e:
            # ✅ Логируем любую другую ошибку
            self.audit.log_analysis(self.skill_id, self.skill_name, target_file, "error")
            return f"⚠️ Непредвиденная ошибка: {str(e)}"
