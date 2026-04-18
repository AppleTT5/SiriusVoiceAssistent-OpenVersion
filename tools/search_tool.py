"""Инструмент для поиска в интернете"""
from typing import Dict, Any
from ddgs import DDGS
from .base import BaseTool, ToolResult

class SearchWebTool(BaseTool):
    """Поиск информации в интернете через DuckDuckGo"""
    
    @property
    def name(self) -> str:
        return "search_web"
    
    @property
    def description(self) -> str:
        return "Ищет актуальную информацию в интернете. Используй для цен, новостей.Используй если пользователь просит найти в интернете и если ты не знаешь ответа"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Поисковый запрос"
            }
        }
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append({
                        'title': r.get('title', ''),
                        'body': r.get('body', ''),
                        'href': r.get('href', '')
                    })
            
            if not results:
                return ToolResult(success=True, content=f"По запросу '{query}' ничего не найдено")
            
            formatted = f"📊 РЕЗУЛЬТАТЫ ПОИСКА: {query}\n\n"
            for i, r in enumerate(results, 1):
                formatted += f"[{i}] {r['title']}\n    {r['body'][:400]}\n    🔗 {r['href']}\n\n"
            
            return ToolResult(success=True, content=formatted)
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))