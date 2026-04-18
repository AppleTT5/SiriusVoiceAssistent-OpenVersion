"""Конфигурация приложения"""
import os
from dataclasses import dataclass
from pathlib import Path
# ============================================================================
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (только для кэша, не для пути модели!)
# ============================================================================



# Создаём папки

@dataclass
class Config:
    # ИСПОЛЬЗУЕМ ИМЯ МОДЕЛИ (как в старой версии)
    model_name: str = "Qwen/Qwen2.5-3B-Instruct"  # ← не путь!
    
    # Генерация
    max_new_tokens: int = 512
    temperature: float = 0.5
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    
    # Память
    memory_file: Path = Path("memory.json")
    memory_ttl_days: int = 30
    
    # Кэш

    
    # Эндпоинты
    host: str = "0.0.0.0"
    port: int = 8000

config = Config()