"""Выполнение вызовов инструментов"""
import re
import json
from typing import Optional, Dict, Any, Tuple
from tools.registry import tool_registry
from tools.base import ToolResult

def parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    """Извлекает вызов инструмента из ответа модели"""
    match = re.search(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

async def execute_tool_call(tool_call: Dict[str, Any]) -> ToolResult:
    """Выполняет вызов инструмента"""
    tool_name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})
    
    tool = tool_registry.get(tool_name)
    if not tool:
        return ToolResult(success=False, content="", error=f"Инструмент '{tool_name}' не найден")
    
    return await tool.execute(**arguments)