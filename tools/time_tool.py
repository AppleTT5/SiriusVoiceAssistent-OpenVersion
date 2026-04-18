"""Инструмент для получения текущего времени"""
from typing import Dict, Any
from datetime import datetime
from .base import BaseTool, ToolResult

class GetTimeTool(BaseTool):
    """Получение текущего времени и даты"""
    
    @property
    def name(self) -> str:
        return "get_time"
    
    @property
    def description(self) -> str:
        return "Получает текущее время и дату."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {}
    
    async def execute(self, **kwargs) -> ToolResult:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ToolResult(success=True, content=current_time)