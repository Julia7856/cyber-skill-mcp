"""
Audit Logger - Журнал аудита для юридической чистоты
Записывает мета-данные каждого анализа, не сохраняя сами файлы
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

class AuditLogger:
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = Path(__file__).parent.parent / log_file
        
    def _calculate_hash(self, file_path: str) -> str:
        """Вычисляет SHA-256 хэш файла (его цифровой отпечаток)"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return "unknown"
            
    def log_analysis(self, skill_id: str, skill_name: str, target_file: str, status: str):
        """Записывает событие анализа в журнал"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_id": skill_id,
            "skill_name": skill_name,
            "target_file_hash": self._calculate_hash(target_file),
            "target_filename": os.path.basename(target_file),
            "status": status  # "success", "error", "blocked"
        }
        
        # Добавляем запись в файл (append mode)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        print(f"📝 Audit Log: Запись добавлена для {os.path.basename(target_file)}")
