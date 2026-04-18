"""Регистр инструментов — центральное место для добавления новых инструментов"""
from typing import Dict, Optional
from .base import BaseTool

class ToolRegistry:
    """Регистр всех доступных инструментов"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Регистрирует инструмент"""
        if tool.name in self._tools:
            print(f"⚠️ Инструмент {tool.name} уже зарегистрирован, перезаписываю")
        self._tools[tool.name] = tool
        print(f"  ✅ Зарегистрирован инструмент: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Возвращает инструмент по имени"""
        return self._tools.get(name)
    
    def get_all(self) -> Dict[str, BaseTool]:
        """Возвращает все инструменты"""
        return self._tools.copy()
    
    def get_tools_description(self) -> str:
        """Возвращает описание всех инструментов для промпта"""
        lines = []
        for tool in self._tools.values():
            lines.append(f"• {tool.name}: {tool.description}")
        return "\n".join(lines)
    
    def get_openai_schemas(self) -> list:
        """Возвращает схемы всех инструментов в формате OpenAI"""
        return [tool.get_openai_schema() for tool in self._tools.values()]

# Глобальный экземпляр регистра
tool_registry = ToolRegistry()