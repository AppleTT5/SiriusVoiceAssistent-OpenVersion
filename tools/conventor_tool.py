from .base import BaseTool, ToolResult
from typing import Dict, Any
import requests

class ConventorTool(BaseTool):
    
    @property
    def name(self) ->str:
        return "convert"
    
    @property
    def description(self) -> str:
        return "Конвертирует валюты, единицы измерения, температуры и т.д."
    
    @property
    def parameters(self) -> Dict[str,Any]:
        return{
            "value": {"type": "number", "description": "Числовое значение"},
                "from_unit": {"type": "string", "description": "Из какой единицы (USD, EUR, km, miles, C, F)"},
                "to_unit": {"type": "string", "description": "В какую единицу конвертировать"}
        } 
    
    async def execute(self,value: float, from_unit: str, to_unit: str,**kwargs):
        if from_unit.upper() in ["USD", "EUR", "RUB"] and to_unit.upper() in ["USD", "EUR", "RUB"]:
            try:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_unit.upper()}"
                response = requests.get(url)
                rate = response.json()["rates"][to_unit.upper()]
                result = value * rate
                return ToolResult(success=True,content=f"{value} {from_unit} = {result:.2f} {to_unit}")
            except:
                return ToolResult(success=False ,content= "Не удалось получить курс валют")
        return ToolResult(success=False,content="Конвертация временно недоступна")