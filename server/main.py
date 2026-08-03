"""
Cyber Skill Router - MCP Server
Sandbox-First архитектура для безопасного реверс-инжиниринга
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import yaml
import os
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))
from sandbox.manager import SandboxManager

app = Server("cyber-skill-router")


def load_skills():
    """Загружает все навыки (YAML-файлы) из папки registry/"""
    skills = {}
    registry_path = Path(__file__).parent.parent / "registry"
    
    if not registry_path.exists():
        print(f"⚠️ Папка реестра не найдена: {registry_path}")
        return skills
    
    for yaml_file in registry_path.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                skill = yaml.safe_load(f)
                if skill and "skill_id" in skill:
                    skills[skill["skill_id"]] = skill
                    print(f"✅ Загружен навык: {skill['name']} ({skill['skill_id']})")
        except Exception as e:
            print(f"❌ Ошибка загрузки {yaml_file}: {e}")
    
    return skills


SKILLS = load_skills()


@app.list_tools()
async def list_tools():
    """Возвращает список всех доступных навыков как инструменты MCP"""
    tools = []
    for skill_id, skill in SKILLS.items():
        tools.append(
            Tool(
                name=skill_id,
                description=f"[{skill['category']}] {skill['description']}",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_file": {
                            "type": "string",
                            "description": "Абсолютный путь к файлу для анализа"
                        },
                        "extra_args": {
                            "type": "string",
                            "description": "Дополнительные аргументы (опционально)",
                            "default": ""
                        }
                    },
                    "required": ["target_file"]
                }
            )
        )
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Вызывается, когда ИИ-агент хочет использовать конкретный навык"""
    if name not in SKILLS:
        return [TextContent(type="text", text=f"❌ Навык '{name}' не найден.")]

    skill = SKILLS[name]
    target = arguments["target_file"]
    
    # Проверка безопасности: путь должен быть абсолютным
    if not os.path.isabs(target):
        return [TextContent(type="text", text=f"⚠️ Пожалуйста, укажите абсолютный путь к файлу.")]
    
    if not os.path.isfile(target):
        return [TextContent(type="text", text=f"❌ Файл не найден: {target}")]

    # Запускаем песочницу
    manager = SandboxManager(skill)
    try:
        result = manager.execute_in_sandbox(target, arguments.get("extra_args", ""))
        return [TextContent(type="text", text=f"✅ Результат анализа:\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"⚠️ Ошибка выполнения: {str(e)}")]


if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        print("🚀 Cyber Skill Router MCP Server запущен")
        print(f"📦 Загружено навыков: {len(SKILLS)}")
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())
    
    asyncio.run(main())
