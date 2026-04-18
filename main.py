"""Главный файл приложения — точка входа"""
import os

from config import config

import asyncio
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from prompts import get_system_prompt
from core.llm_client import LLMClient
from core.tool_executor import parse_tool_call, execute_tool_call
from tools.registry import tool_registry
from tools.search_tool import SearchWebTool
from tools.time_tool import GetTimeTool
from tools.memory_tool import (
    ListMemoryTool, LoadMemoryTool, WriteMemoryTool, DeleteMemoryTool
)
from models.schemas import ChatRequest, ChatResponse
from tools.weather_tool import WeatherTool
from tools.random_tool import RandomTool
from tools.conventor_tool import ConventorTool
# ============================================================================
# ИНИЦИАЛИЗАЦИЯ (выполняется один раз при старте)
# ============================================================================

print("\n" + "=" * 60)
print("🤖 SIRIUS ASSISTANT v2.0 (МОДУЛЬНАЯ АРХИТЕКТУРА)")
print("=" * 60)

# 1. Регистрируем все инструменты
print("\n🔧 РЕГИСТРАЦИЯ ИНСТРУМЕНТОВ")
tool_registry.register(SearchWebTool())
tool_registry.register(GetTimeTool())
#tool_registry.register(ListMemoryTool(config.memory_file))
#tool_registry.register(LoadMemoryTool(config.memory_file))
#tool_registry.register(WriteMemoryTool(config.memory_file, config.memory_ttl_days))
#tool_registry.register(DeleteMemoryTool(config.memory_file))
tool_registry.register(WeatherTool())
tool_registry.register(RandomTool())
tool_registry.register(ConventorTool())

# 2. Загружаем LLM (только один раз)
llm_client = LLMClient(config.model_name,)

# 3. Создаём FastAPI приложение
app = FastAPI(title="Sirius Assistant API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def build_prompt(user_input: str, history: list) -> str:
    """Строит промпт для модели"""
    tools_desc = tool_registry.get_tools_description()
    system_prompt = get_system_prompt(tools_desc)
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    
    return llm_client.tokenizer.apply_chat_template(
        messages,
        tools=tool_registry.get_openai_schemas(),
        tokenize=False,
        add_generation_prompt=True
    )

async def generate_response(user_input: str, history: list, max_iterations: int = 3) -> str:
    """Генерирует ответ с возможностью вызова инструментов"""
    current_input = user_input
    current_history = history.copy()
    
    for iteration in range(max_iterations):
        prompt = build_prompt(current_input, current_history)
        response = llm_client.generate(prompt)
        
        tool_call = parse_tool_call(response)
        
        if not tool_call:
            return response if response else "Извините, я не знаю, что ответить."
        
        # Выполняем инструмент
        result = await execute_tool_call(tool_call)
        
        if not result.success:
            current_input = f"Ошибка при выполнении {tool_call.get('name')}: {result.error}"
            continue
        
        # Добавляем результат в контекст для следующей итерации
        current_history.append({"role": "assistant", "content": f"[Результат: {result.content[:200]}]"})
        current_input = f"""На основе результата выполнения инструмента '{tool_call.get('name')}', ответь пользователю.

Результат: {result.content}

Вопрос пользователя: {user_input}

Ответь кратко, используя эту информацию."""
    
    return "Не удалось получить ответ после нескольких попыток."

# ============================================================================
# ПАМЯТЬ ДИАЛОГОВ (простая)
# ============================================================================

class ConversationMemory:
    def __init__(self, max_messages=20):
        self.max_messages = max_messages
        self.messages = {}
    
    def get_history(self, user_id: str) -> list:
        if user_id not in self.messages:
            self.messages[user_id] = []
        return self.messages[user_id].copy()
    
    def add_user(self, user_id: str, content: str):
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append({"role": "user", "content": content})
        if len(self.messages[user_id]) > self.max_messages:
            self.messages[user_id] = self.messages[user_id][-self.max_messages:]
    
    def add_assistant(self, user_id: str, content: str):
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append({"role": "assistant", "content": content})
        if len(self.messages[user_id]) > self.max_messages:
            self.messages[user_id] = self.messages[user_id][-self.max_messages:]

conv_memory = ConversationMemory()

# ============================================================================
# API ЭНДПОИНТЫ
# ============================================================================

@app.get("/")
async def root():
    return {"message": "Sirius Assistant API v2.0", "status": "active"}

@app.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest):
    start_time = time.time()
    
    try:
        print(f"\n👤 [{request.user_id}]: {request.text}")
        
        conv_memory.add_user(request.user_id, request.text)
        history = conv_memory.get_history(request.user_id)[:-1]
        
        response = await generate_response(request.text, history)
        
        conv_memory.add_assistant(request.user_id, response)
        
        processing_time = time.time() - start_time
        print(f"🤖 [{request.user_id}]: {response[:100]}... (⏱️ {processing_time:.2f}с)")
        
        return ChatResponse(response=response, user_id=request.user_id, processing_time=processing_time)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "device": str(llm_client.device)}

@app.get("/stats")
async def get_stats():
    """Статистика о модели и инструментах"""
    return {
        "model_loaded": llm_client.model is not None,
        "device": str(llm_client.device),
        "tools_count": len(tool_registry.get_all()),
        "tools": list(tool_registry.get_all().keys())
    }

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    print(f"\n  🚀 Устройство: {llm_client.device}")
    print(f"  📡 API: http://{config.host}:{config.port}")
    print(f"  🔧 Инструментов: {len(tool_registry.get_all())}")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host=config.host, 
        port=config.port, 
        log_level="info",
        reload=False  # ← ВАЖНО: отключаем autoreload, чтобы модель не перезагружалась
    )
