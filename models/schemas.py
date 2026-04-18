"""Pydantic модели для данных"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ToolCall(BaseModel):
    """Модель вызова инструмента"""
    name: str
    arguments: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    """Ответ от инструмента"""
    success: bool
    content: str
    error: Optional[str] = None

class ChatRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    user_id: str
    processing_time: Optional[float] = None

class MemoryCell(BaseModel):
    """Ячейка памяти"""
    text: str
    facts: Dict[str, Any]
    created: datetime
    expires: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl_days: int = 130