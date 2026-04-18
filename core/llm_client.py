"""Клиент для работы с LLM"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional
from pathlib import Path

class LLMClient:
    _instance: Optional['LLMClient'] = None
    _model = None
    _tokenizer = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str):  # ← убрали cache_dir
        if LLMClient._model is not None:
            print(f"✅ МОДЕЛЬ УЖЕ ЗАГРУЖЕНА")
            return
        
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_model()
    
    def _load_model(self):
        print(f"\n📥 ЗАГРУЗКА МОДЕЛИ: {self.model_name}")
        
        # Переменные окружения уже установлены в main.py
        LLMClient._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        LLMClient._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        if LLMClient._tokenizer.pad_token is None:
            LLMClient._tokenizer.pad_token = LLMClient._tokenizer.eos_token
        
        print(f"✅ МОДЕЛЬ ЗАГРУЖЕНА (устройство: {self.device})")
    
    @property
    def model(self):
        return LLMClient._model
    
    @property
    def tokenizer(self):
        return LLMClient._tokenizer
    
    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get('max_new_tokens', 512),
                temperature=kwargs.get('temperature', 0.5),
                do_sample=True,
                top_p=kwargs.get('top_p', 0.9),
                repetition_penalty=kwargs.get('repetition_penalty', 1.1),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)