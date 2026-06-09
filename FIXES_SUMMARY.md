# Исправления и изменения проекта

## Критические исправления

### 1. Удаление дублирующегося кода в `rag/query.py`
**Проблема:** Дублирование блоков кода после `return response` вызывало синтаксическую ошибку.
**Исправление:** Удалены дублирующиеся строки кода (строки 58-70).

### 2. Устранение циклического импорта между `handlers/text.py` и `handlers/hr.py`
**Проблема:** `handlers/text.py` импортировал `_is_hr_question` из `handlers/hr.py`, а `handlers/hr.py` импортировал `route_hr_request` из `services/router.py`, что могло вызвать циклический импорт.
**Исправление:**
- Функция `_is_hr_question` перемещена в `utils/helpers.py` как `is_hr_question()`
- `handlers/text.py` теперь импортирует `is_hr_question` из `utils.helpers`
- `handlers/hr.py` содержит обертку `_is_hr_question()` для обратной совместимости

### 3. Обновление тестов в `tests/test_hr.py`
**Проблема:** Тесты использовали локальную копию `_is_hr_question`.
**Исправление:** Тесты теперь импортируют `is_hr_question` из `utils.helpers`.

## Структура проекта

```
├── bot.py                 # Основной экземпляр бота
├── main.py               # Точка входа
├── config.py             # Конфигурация
├── requirements.txt      # Зависимости
├── .env.example          # Пример переменных окружения
├── handlers/             # Обработчики команд
│   ├── start.py         # /start, /help команды
│   ├── text.py          # Текстовые сообщения
│   ├── voice.py         # Голосовые сообщения
│   ├── image.py         # Анализ изображений
│   ├── hr.py            # HR-ассистент
│   └── document_upload.py # Загрузка документов
├── services/             # Сервисы
│   ├── openai_client.py # OpenAI API клиент
│   ├── router.py        # Роутинг запросов
│   ├── stt.py           # Speech-to-Text
│   ├── tts.py           # Text-to-Speech
│   ├── vision.py        # Анализ изображений
│   ├── image_generation.py # Генерация изображений
│   └── hr_assistant.py  # HR-ассистент клиент
├── rag/                  # RAG функциональность
│   ├── loader.py        # Загрузка документов
│   ├── index.py         # Векторный индекс
│   └── query.py         # Запросы к базе знаний
├── utils/                # Утилиты
│   ├── helpers.py       # Вспомогательные функции
│   └── logging.py       # Логирование
└── tests/                # Тесты
    ├── test_text.py
    ├── test_hr.py
    ├── test_rag.py
    ├── test_stt.py
    └── test_image_generation.py
```

## Возможности бота

1. **Текстовый режим** - GPT-4o для общих вопросов
2. **Голосовой режим** - STT + TTS для голосовых сообщений
3. **Анализ изображений** - GPT-4 Vision для анализа фото
4. **RAG** - База знаний с поиском по документам
5. **HR-ассистент** - Специализированный помощник для новичков
6. **Генерация изображений** - DALL-E 3 для создания картинок

## Команды

- `/start` - Приветствие
- `/help` - Справка
- `/mode <режим>` - Переключение режима (text/voice/vision/rag/hr)
- `/voice <голос>` - Выбор голоса для TTS
- `/reset` - Очистка истории
- `/stats` - Статистика базы знаний
- `/hr` - Справка HR-ассистента
- `/hr/reset` - Сброс контекста HR
- `/hr/status` - Статус онбординга
- `/image <промпт>` - Генерация изображения

## Запуск

1. Скопируйте `.env.example` в `.env` и заполните переменные
2. Установите зависимости: `pip install -r requirements.txt`
3. Запустите бота: `python main.py`

## Тестирование

Запуск всех тестов:
```bash
pytest tests/ -v
```

Запуск конкретных тестов:
```bash
pytest tests/test_hr.py -v
pytest tests/test_rag.py -v
pytest tests/test_image_generation.py -v
```
