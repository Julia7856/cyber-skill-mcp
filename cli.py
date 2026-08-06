"""
CLI Interface - Командная строка для быстрого запуска анализа
Использование: python cli.py analyze app.apk --skill apk_reverse_001
"""

import argparse
import sys
import os
from pathlib import Path
from server.main import SKILLS
from sandbox.manager import SandboxManager

def analyze_file(target_file: str, skill_id: str):
    """Запускает анализ файла через указанный навык"""
    # Проверяем существование файла
    if not os.path.isfile(target_file):
        print(f"❌ Файл не найден: {target_file}")
        sys.exit(1)
    
    # Проверяем наличие навыка
    if skill_id not in SKILLS:
        print(f"❌ Навык '{skill_id}' не найден.")
        print(f"📋 Доступные навыки: {', '.join(SKILLS.keys())}")
        sys.exit(1)
    
    skill = SKILLS[skill_id]
    print(f" Запуск анализа: {skill['name']}")
    print(f"📁 Файл: {target_file}")
    print(f" Режим: Изолированная песочница")
    print("-" * 50)
    
    # Запускаем песочницу
    manager = SandboxManager(skill)
    try:
        result = manager.execute_in_sandbox(target_file)
        print("\n" + "=" * 50)
        print("✅ РЕЗУЛЬТАТ АНАЛИЗА:")
        print("=" * 50)
        print(result)
        print("\n📝 Audit Log обновлен: audit.log")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

def list_skills():
    """Выводит список всех доступных навыков"""
    print("📋 Доступные навыки:\n")
    for skill_id, skill in SKILLS.items():
        print(f"  • {skill_id}")
        print(f"    Название: {skill['name']}")
        print(f"    Категория: {skill['category']}")
        print(f"    Описание: {skill['description']}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description="Cyber Skill Router - CLI интерфейс",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python cli.py list                          # Показать все навыки
  python cli.py analyze app.apk --skill apk_reverse_001
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда: list
    subparsers.add_parser("list", help="Показать список всех навыков")
    
    # Команда: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Запустить анализ файла")
    analyze_parser.add_argument("target_file", help="Путь к файлу для анализа")
    analyze_parser.add_argument("--skill", required=True, help="ID навыка (например: apk_reverse_001)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_skills()
    elif args.command == "analyze":
        analyze_file(args.target_file, args.skill)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
