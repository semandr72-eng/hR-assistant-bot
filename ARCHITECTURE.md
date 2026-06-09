# Архитектура Telegram-бота HR-ассистента

## 📋 Обзор

Проект представляет собой мультимодального AI-ассистента для корпоративной поддержки сотрудников с использованием технологии Retrieval-Augmented Generation (RAG).

## 🏗️ Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Пользователь (Telegram)                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                    Telegram Bot API
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                         bot.py (AsyncTeleBot)                       │
│                     - Асинхронный Telegram клиент                    │
│                     - Маршрутизация сообщений                        │
│                     - Управление сессиями                            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┬─────────────────────┐
         │                 │                 │                     │
┌────────▼──────┐  ┌──────▼──────┐  ┌───────▼───────┐  ┌──────────▼──────┐
│  handlers/    │  │  services/  │  │    rag/       │  │    utils/       │
│               │  │             │  │               │  │                 │
│ - start.py    │  │ - router.py │  │ - loader.py   │  │ - helpers.py    │
│ - text.py     │  │ - stt.py    │  │ - index.py    │  │ - logging.py    │
│ - voice.py    │  │ - tts.py    │  │ - query.py    │  │                 │
│ - image.py    │  │ - vision.py │  │               │  │                 │
│ - hr.py       │  │ - openai_   │  │               │  │                 │
│               │  │   client.py │  │               │  │                 │
└───────────────┘  └──────┬──────┘  └───────┬───────┘  └─────────────────┘
                          │                 │
                          └────────┬────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │       OpenAI API Client     │
                    │                             │
                    │  - GPT-4o (текст)           │
                    │  - Whisper (STT)            │
                    │  - TTS-1 (синтез речи)      │
                    │  - GPT-4 Vision (анализ)    │
                    │  - DALL-E 3 (генерация)     │
                    │  - Embeddings (векторы)     │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │        ChromaDB             │
                    │  (Векторная база данных)    │
                    │                             │
                    │  - Локальное SQLite         │
                    │  - 1536 измерений           │
                    │  - Cosine Similarity        │
                    └─────────────────────────────┘
```

## 🔄 Поток обработки запроса

### 1. Текстовый запрос

```
Пользователь → Сообщение в Telegram
                    │
                    ▼
         handlers/text.py (handle_text_message)
                    │
                    ▼
          services/router.py (route_text_request)
                    │
                    ▼
          ПРОВЕРКА: Запрос на генерацию изображения?
         ┌──────────┴──────────┐
         │                     │
        ДА                    НЕТ
         │                     │
         ▼                     ▼
route_image_generation   query_knowledge_base
         │                     │
         │                     ▼
         │           rag.query.py (query_knowledge_base)
         │                     │
         │                     ▼
         │          vector_index.similarity_search()
         │                     │
         │                     ▼
         │          Подбор релевантных чанков
         │                     │
         │                     ▼
         │          _generate_rag_response()
         │          (GPT-4o с контекстом)
         │                     │
         └───────────┬─────────┘
                     │
                     ▼
              Ответ пользователю
```

### 2. Голосовой запрос

```
Пользователь → Голосовое сообщение
                    │
                    ▼
         handlers/voice.py (handle_voice_message)
                    │
                    ▼
          services/router.py (route_voice_request)
                    │
                    ▼
          services/stt.py (transcribe_voice_message)
                    │
                    ▼
          OpenAI Whisper API → Текст
                    │
                    ▼
          (Далее как текстовый запрос)
                    │
                    ▼
          services/tts.py (generate_voice_response)
                    │
                    ▼
          OpenAI TTS API → Аудио
                    │
                    ▼
           Ответ: Текст + Голос
```

### 3. Анализ изображения

```
Пользователь → Фото + подпись
                    │
                    ▼
         handlers/image.py (handle_photo_message)
                    │
                    ▼
          services/router.py (route_image_request)
                    │
                    ▼
          services/vision.py (analyze_image)
                    │
                    ▼
          OpenAI GPT-4 Vision API
                    │
                    ▼
          Анализ изображения
                    │
                    ▼
           Ответ с описанием
```

## 📦 Модульная структура

### handlers/ - Обработчики команд

| Файл | Назначение | Ключевые функции |
|------|------------|------------------|
| `start.py` | Команды /start, /help, /reset | `cmd_start()`, `cmd_help()` |
| `text.py` | Текстовые сообщения | `handle_text_message()`, `cmd_mode()` |
| `voice.py` | Голосовые сообщения | `handle_voice_message()`, `cmd_voice()` |
| `image.py` | Изображения | `handle_photo_message()` |
| `hr.py` | HR-ассистент | `handle_hr_message()`, `cmd_hr()` |
| `document_upload.py` | Загрузка документов | `process_document_upload()` |

### services/ - Сервисы

| Файл | Назначение | Ключевые классы |
|------|------------|-----------------|
| `openai_client.py` | OpenAI API клиент | `OpenAIClient` |
| `router.py` | Маршрутизация запросов | `route_text_request()`, `route_voice_request()` |
| `stt.py` | Распознавание речи | `transcribe_voice_message()` |
| `tts.py` | Синтез речи | `generate_voice_response()` |
| `vision.py` | Анализ изображений | `analyze_image()` |
| `image_generation.py` | Генерация изображений | `generate_image()`, `detect_image_generation_intent()` |
| `hr_assistant.py` | HR-специализированный клиент | `HRAssistantClient` |

### rag/ - RAG функциональность

| Файл | Назначение | Ключевые классы |
|------|------------|-----------------|
| `loader.py` | Загрузка документов | `DocumentLoader` |
| `index.py` | Векторный индекс | `VectorIndex` |
| `query.py` | Запросы к базе знаний | `query_knowledge_base()`, `_generate_rag_response()` |

### utils/ - Утилиты

| Файл | Назначение | Ключевые функции |
|------|------------|------------------|
| `helpers.py` | Вспомогательные функции | `UserSession`, `is_hr_question()`, `save_file_async()` |
| `logging.py` | Логирование | `ColoredFormatter`, `logger` |

## 🗄️ Хранение данных

### Структура данных

```
data/
├── documents/              # Исходные документы для RAG
│   ├── auchan_rules.txt
│   └── company_info.txt
├── chroma_db/              # Векторная база данных
│   ├── chroma.sqlite3      # SQLite индекс ChromaDB
│   └── <uuid>/             # Коллекция с эмбеддингами
└── generated_images/       # Сгенерированные изображения
    └── generated_<timestamp>.png
```

### ChromaDB конфигурация

- **Тип хранилища:** Local Persistent
- **Бэкенд:** SQLite
- **Путь:** `data/chroma_db/`
- **Размер эмбеддинга:** 1536 измерений
- **Метрика сходства:** Cosine Similarity

## 🔐 Безопасность

### Управление секретами

```python
# config.py
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

**Важно:** Файл `.env` НЕ коммитится в Git (.gitignore)

### Обработка ошибок

```python
try:
    response = await openai_client.generate_text_response(messages)
except Exception as e:
    logger.error(f"Error generating response: {e}")
    return "Извините, произошла ошибка."
```

## ⚡ Асинхронность

Весь код построен на `asyncio`:

```python
# bot.py
from telebot.async_telebot import AsyncTeleBot
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)

# handlers
@bot.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await bot.send_message(message.chat.id, "Привет!")
```

## 🧠 RAG Pipeline

### 1. Загрузка документов

```python
# rag/loader.py
class DocumentLoader:
    def load_document(self, file_path: Path) -> List[Document]:
        # PDF через pdfplumber
        # TXT/MD через TextLoader
        # Чанкинг через RecursiveCharacterTextSplitter
```

### 2. Векторизация

```python
# rag/index.py
self.embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)
```

### 3. Индексация

```python
# ChromaDB
self.vectorstore = Chroma(
    persist_directory=str(self.persist_directory),
    embedding_function=self.embeddings
)
self.vectorstore.add_documents(documents)
```

### 4. Поиск

```python
results = vector_index.similarity_search_with_score(query, k=3)
```

### 5. Генерация ответа

```python
system_prompt = """Ты - HR-ассистент компании Ашан...
КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {query}"""

response = await openai_client.generate_text_response(messages)
```

## 🎯 Ключевые особенности

### 1. Автоматическое определение намерений

```python
# services/image_generation.py
async def detect_image_generation_intent(text: str, history: list):
    # Анализ через GPT + ключевые слова
    # Возвращает: needs_generation, prompt, confidence
```

### 2. HR-детекция

```python
# utils/helpers.py
def is_hr_question(text: str) -> bool:
    hr_keywords = ['отпуск', 'зарплата', 'больничный', ...]
    return any(keyword in text.lower() for keyword in hr_keywords)
```

### 3. Управление сессиями

```python
# utils/helpers.py
class UserSession:
    def get_history(self, user_id: int) -> list
    def add_message(self, user_id: int, role: str, content: str)
    def get_mode(self, user_id: int) -> str
    def set_mode(self, user_id: int, mode: str)
```

## 📊 Производительность

### Оптимизации

1. **Асинхронные вызовы** - все API вызовы async/await
2. **Кэширование сессий** - история в памяти
3. **Локальная БД** - ChromaDB без сетевого задержек
4. **Ленивая загрузка** - импорты по требованию
5. **Автоочистка** - временные файлы удаляются

### Метрики

- **Время ответа (текст):** ~2-5 секунд
- **Время распознавания (голос):** ~1-2 секунды
- **Время синтеза (голос):** ~1-2 секунды
- **Время поиска (RAG):** ~0.5-1 секунда
- **Время генерации (изображение):** ~10-30 секунд

## 🚀 Масштабируемость

### Горизонтальное масштабирование

- Бесстатусные обработчики
- Внешнее хранилище документов
- ChromaDB в режиме сервера (опционально)

### Вертикальное масштабирование

- Увеличение chunk_size для больших документов
- Увеличение top_k для более точных ответов
- Кэширование частых запросов

## 🔧 Конфигурация

### config.py

```python
# RAG Configuration
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_TOP_K = 3

# OpenAI Settings
TEMPERATURE = 0.7
MAX_TOKENS = 1500

# User session settings
MAX_HISTORY_LENGTH = 10
```

## 📝 Расширяемость

### Добавление нового сервиса

```python
# services/new_service.py
class NewServiceClient:
    async def process(self, data: str) -> str:
        # Реализация
        pass

new_service = NewServiceClient()
```

### Добавление нового обработчика

```python
# handlers/new_handler.py
@bot.message_handler(commands=['new'])
async def cmd_new(message: types.Message):
    # Обработка
    pass
```

---

**Версия:** 1.0.0  
**Дата:** 2024  
**Команда:** NLP-Core-Team
