from .base import BaseTool, ToolResult
from typing import Dict, Any
import requests
class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "Get_Weather"
    
    @property
    def description(self) ->str:
        return "С помощью этого инструмента ты можешь узнавать погоду сейчас.Используй если пользователь просит данные о погоде температуре влажности или других погодных явлениях"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "(только если пользователь добавил) город про который спрашивают погоду (не обязательно)"}
        }
    
    async def execute(self, query: str ="балашиха", **kwargs)->ToolResult:
        city = query
        #city = "балашиха"
        try:
            response = requests.get(f"https://wttr.in/{city}?format=%C+%t%w%h%P")
            return ToolResult(success=True,content=f"Погода в {city}: {response.text.strip()}")
        except:
            return ToolResult(success=False,content=f"Не удалось получить погоду для {city}")