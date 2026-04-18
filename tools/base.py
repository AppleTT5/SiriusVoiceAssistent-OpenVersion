"""Базовый класс для всех инструментов"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class ToolResult:
    """Результат выполнения инструмента"""
    success: bool
    content: str
    error: Optional[str] = None
    execution_time: float = 0.0

class BaseTool(ABC):
    """Абстрактный базовый класс для всех инструментов"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя инструмента (должно совпадать с тем, что ожидает модель)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Описание для промпта"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Схема параметров для JSON Schema"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Выполнение инструмента"""
        pass
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Возвращает схему в формате OpenAI function calling"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters.keys())
                }
            }
        }