from .base import BaseTool, ToolResult
from typing import Dict, Any

import random
import string

class RandomTool(BaseTool):
    @property
    def name(self) ->str:
        return "generate_random"
    
    @property
    def description(self) -> str:
        return "Генерирует случайные числа, пароли, имена или другие данные."
    
    @property
    def parameters(self) -> dict[str,Any]:
        return {
            "type": {
                    "type": "string",
                    "enum": ["number", "password", "name"],
                    "description": "Тип генерации"
                    },
            "length": {
                    "type": "integer",
                    "description": "Длина (для пароля или количества чисел)"
                },
                "min": {"type": "integer", "description": "Минимум (для чисел)"},
                "max": {"type": "integer", "description": "Максимум (для чисел)"}
        }
    
    async def execute(self,type: str, length: int = 8, min_val: int = 0, max_val: int = 100, **kwargs) ->ToolResult:
        if type == "number":
            return ToolResult(success=True,content= f"Случайное число: {random.randint(min_val, max_val)}")
        elif type == "password":
            chars = string.ascii_letters + string.digits
            password = ''.join(random.choice(chars) for _ in range(length))
            return ToolResult( success=True,content=f"Сгенерированный пароль: {password}")
        elif type == "name":
            names = ["Алексей", "Мария", "Дмитрий", "Анна", "Сергей", "Екатерина", "Владимир", "Ольга"]
            return ToolResult(success=True,content=f"Случайное имя: {random.choice(names)}")
        return ToolResult(success=False,content="Неизвестный тип генерации")