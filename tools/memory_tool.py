"""Инструменты для работы с памятью"""
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from .base import BaseTool, ToolResult

class ListMemoryTool(BaseTool):
    """Показывает список всех ячеек памяти"""
    
    def __init__(self, memory_file: Path):
        self.memory_file = memory_file
    
    @property
    def name(self) -> str:
        return "list_memory"
    
    @property
    def description(self) -> str:
        return "Показывает список всех сохранённых ячеек памяти."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {}
    
    async def execute(self, **kwargs) -> ToolResult:
        memory = self._load_memory()
        if not memory:
            return ToolResult(success=True, content="Память пуста")
        
        cells = list(memory.keys())
        return ToolResult(success=True, content=f"Доступные ячейки: {', '.join(cells)}")
    
    def _load_memory(self) -> dict:
        if not self.memory_file.exists():
            return {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)

class LoadMemoryTool(BaseTool):
    """Загружает данные из ячейки памяти"""
    
    def __init__(self, memory_file: Path):
        self.memory_file = memory_file
    
    @property
    def name(self) -> str:
        return "load_memory"
    
    @property
    def description(self) -> str:
        return "Загружает данные из указанной ячейки памяти."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "cell_name": {
                "type": "string",
                "description": "Название ячейки памяти"
            }
        }
    
    async def execute(self, cell_name: str, **kwargs) -> ToolResult:
        memory = self._load_memory()
        if cell_name not in memory:
            return ToolResult(success=False, content="", error=f"Ячейка '{cell_name}' не найдена")
        
        cell = memory[cell_name]
        text = cell.get('text', '') if isinstance(cell, dict) else str(cell)
        return ToolResult(success=True, content=text)
    
    def _load_memory(self) -> dict:
        if not self.memory_file.exists():
            return {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)

class WriteMemoryTool(BaseTool):
    """Записывает данные в ячейку памяти"""
    
    def __init__(self, memory_file: Path, ttl_days: int = 30):
        self.memory_file = memory_file
        self.ttl_days = ttl_days
    
    @property
    def name(self) -> str:
        return "write_memory"
    
    @property
    def description(self) -> str:
        return "Сохраняет данные в ячейку памяти."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "cell_name": {
                "type": "string",
                "description": "Название ячейки"
            },
            "data": {
                "type": "string",
                "description": "Данные для сохранения"
            }
        }
    
    async def execute(self, cell_name: str, data: str, **kwargs) -> ToolResult:
        memory = self._load_memory()
        
        memory[cell_name] = {
            "text": data,
            "facts": self._extract_facts(data),
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=self.ttl_days)).isoformat(),
            "access_count": 0,
            "ttl_days": self.ttl_days
        }
        
        self._save_memory(memory)
        return ToolResult(success=True, content=f"Сохранено в ячейку '{cell_name}'")
    
    def _extract_facts(self, text: str) -> dict:
        """Извлекает ключевые факты из текста"""
        import re
        facts = {
            "keywords": [],
            "dates": [],
            "numbers": []
        }
        
        # Ключевые слова (слова длиной >3)
        words = re.findall(r'\b[а-яА-ЯёЁ]{3,}\b', text.lower())
        stop_words = {'этот', 'такой', 'который', 'потому', 'поэтому'}
        facts["keywords"] = [w for w in words if w not in stop_words][:10]
        
        # Даты
        date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{2}\.\d{2}\.\d{4}']
        for pattern in date_patterns:
            facts["dates"].extend(re.findall(pattern, text))
        facts["dates"] = list(dict.fromkeys(facts["dates"]))[:3]
        
        return facts
    
    def _load_memory(self) -> dict:
        if not self.memory_file.exists():
            return {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_memory(self, memory: dict):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

class DeleteMemoryTool(BaseTool):
    """Удаляет ячейку памяти"""
    
    def __init__(self, memory_file: Path):
        self.memory_file = memory_file
    
    @property
    def name(self) -> str:
        return "delete_memory"
    
    @property
    def description(self) -> str:
        return "Удаляет указанную ячейку памяти."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "cell_name": {
                "type": "string",
                "description": "Название ячейки для удаления"
            }
        }
    
    async def execute(self, cell_name: str, **kwargs) -> ToolResult:
        memory = self._load_memory()
        if cell_name in memory:
            del memory[cell_name]
            self._save_memory(memory)
            return ToolResult(success=True, content=f"Ячейка '{cell_name}' удалена")
        return ToolResult(success=False, content="", error=f"Ячейка '{cell_name}' не найдена")
    
    def _load_memory(self) -> dict:
        if not self.memory_file.exists():
            return {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_memory(self, memory: dict):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)