import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import traceback
import sys

def ensure_directory_exists(directory):
    """Создает папку если её нет и проверяет права доступа"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Папка {directory} создана")
        else:
            print(f"✅ Папка {directory} уже существует")
        
        # Проверяем права на запись
        test_file = os.path.join(directory, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Права на запись в {directory} проверены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания папки {directory}: {e}")
        return False

def load_facts():
    """Загружает базу фактов из файла БЕЗ обрезания"""
    try:
        print("🔄 Загружаем файл Facts.txt...")
        if not os.path.exists('Facts.txt'):
            print("⚠️ Файл Facts.txt не найден, создаем базовую версию...")
            default_facts = """
Это базовая информация для анализа российских новостей:

ЭКОНОМИКА:
- Россия экспортирует нефть, газ, зерно
- Рубль зависит от цен на энергоресурсы  
- Санкции влияют на торговлю и финансы

ПОЛИТИКА:
- Федеративное устройство с 85 субъектами
- Президентская республика
- Государственная Дума и Совет Федерации

ОБЩЕСТВО:
- Население около 146 млн человек
- Многонациональная страна
- Развитая система образования и здравоохранения

МЕЖДУНАРОДНЫЕ ОТНОШЕНИЯ:
- Член ООН, БРИКС, ШОС, ЕАЭС
- Отношения с Китаем, Индией, странами Африки
- Сложные отношения с Западом
            """
            with open('Facts.txt', 'w', encoding='utf-8') as f:
                f.write(default_facts.strip())
            print("✅ Создан базовый файл Facts.txt")
            return default_facts.strip()
            
        with open('Facts.txt', 'r', encoding='utf-8') as f:
            facts = f.read()
        
        print(f"✅ Загружена база фактов ПОЛНОСТЬЮ ({len(facts)} символов)")
        print(f"📊 Размер файла: {len(facts)/1024/1024:.2f} МБ")
        return facts
        
    except Exception as e:
        print(f"❌ Ошибка работы с Facts.txt: {e}")
        return "Базовые знания для анализа новостей."

def get_available_models():
    """Получает список доступных моделей Gemini"""
    try:
        print("🔄 Проверяем доступные модели Gemini...")
        models = genai.list_models()
        available_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"✅ Доступная модель: {model.name}")
        
        return available_models
    except Exception as e:
        print(f"❌ Ошибка получения списка моделей: {e}")
        return []

def get_news():
    """Получает последние новости с новостных сайтов"""
    print("🔄 Начинаем получение новостей...")
