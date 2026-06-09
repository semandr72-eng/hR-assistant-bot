"""
HR Assistant Handler.
Handles HR-specific queries for new employees using RAG knowledge base.
"""

from telebot import types
from bot import bot
from services.router import route_hr_request
from utils.logging import logger
from utils.helpers import user_sessions
from config import BotMode


@bot.message_handler(commands=['hr'])
async def cmd_hr(message: types.Message):
    """Handle /hr command - HR assistant help."""
    help_text = """👔 **HR-ассистент для новичков**

Привет! Я помогу тебе адаптироваться на новой работе и отвечу на вопросы.

**Что я умею:**
• 📚 Ответы на вопросы о компании
• 📋 Информация о процессах и процедурах
• 💼 Правила и политики
• 🎯 Онбординг и адаптация
• 📝 Документооборот
• 🤝 Корпоративная культура

**Как пользоваться:**
Просто задай вопрос в чате, например:
• «Как оформить отпуск?»
• «К кому обратиться за помощью?»
• «Как работает система оценки?»
• «Где найти правила компании?»

**Команды:**
/hr - Показать эту справку
/hr/reset - Сбросить контекст диалога
/hr/status - Показать статус онбординга

Я отвечаю на основе базы знаний компании. Если не знаю ответа - подскажу, к кому обратиться."""
    
    await bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['hr_reset'])
async def cmd_hr_reset(message: types.Message):
    """Handle /hr_reset command - reset HR conversation."""
    user_id = message.from_user.id
    
    user_sessions.clear_history(user_id)
    logger.info(f"HR conversation reset for user {user_id}")
    
    await bot.send_message(
        message.chat.id,
        "✅ Контекст диалога сброшен!\n\n"
        "Задавай новые вопросы по адаптации и работе в компании."
    )


@bot.message_handler(commands=['hr_status'])
async def cmd_hr_status(message: types.Message):
    """Handle /hr_status command - show onboarding status."""
    user_id = message.from_user.id
    
    # Get user onboarding status
    onboarding_data = user_sessions.get_onboarding_status(user_id)
    
    if not onboarding_data:
        status_text = """📊 **Статус онбординга**

Похоже, ты только начал знакомство с компанией!

**Рекомендуемый порядок:**
1. ✅ Познакомься с HR-ассистентом (/hr)
2. 📖 Изучи базовые правила компании
3. 💼 Разберись с процессами
4. 🎯 Поставь цели с руководителем

Задай вопрос HR-ассистенту, чтобы начать!"""
    else:
        progress = onboarding_data.get('progress', 0)
        questions_count = onboarding_data.get('questions_count', 0)
        last_query = onboarding_data.get('last_query', 'Не задан')
        
        status_text = f"""📊 **Статус онбординга**

Прогресс: {progress}%
Зададено вопросов: {questions_count}

**Последний вопрос:**
{last_query[:100]}...

**Дальнейшие шаги:**
• Продолжай задавать вопросы HR-ассистенту
• Изучай базу знаний компании
• Обращайся за помощью при необходимости"""
    
    await bot.send_message(message.chat.id, status_text)


@bot.message_handler(func=lambda message: user_sessions.get_mode(message.from_user.id) == BotMode.HR)
async def handle_hr_message(message: types.Message):
    """Handle HR-related messages in HR mode."""
    user_id = message.from_user.id
    text = message.text
    
    logger.info(f"HR message from user {user_id}: {text[:50]}...")
    
    # Show typing indicator
    await bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Route HR request
        response = await route_hr_request(user_id, text)
        
        # Update onboarding status
        user_sessions.update_onboarding_status(
            user_id,
            question=text,
            answered=True
        )
        
        # Send response
        response_text = response["text"]
        
        # Add HR-specific footer if not present
        if "💡" not in response_text and "👔" not in response_text:
            response_text += "\n\n💡 *Если вопрос не решён - обратись к своему руководителю или в HR-отдел*"
        
        await bot.send_message(
            message.chat.id,
            response_text,
            parse_mode="Markdown"
        )
    
    except Exception as e:
        logger.error(f"Error handling HR message: {e}", exc_info=True)
        await bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при обработке запроса.\n\n"
            "Попробуйте перефразировать вопрос или обратитесь к руководителю.\n\n"
            "*Совет: используйте /hr для просмотра справки*"
        )


# Auto-detect HR questions in any mode
@bot.message_handler(func=lambda message: _is_hr_question(message.text))
async def handle_hr_question_auto(message: types.Message):
    """Auto-detect HR questions and respond accordingly."""
    # Only handle if user has HR mode enabled or explicitly asks about HR
    user_id = message.from_user.id
    text = message.text.lower()
    
    # Check if this looks like an HR question
    if _is_hr_question(text):
        # Don't intercept if user explicitly wants another mode
        mode = user_sessions.get_mode(user_id)
        if mode in [BotMode.TEXT, BotMode.HR]:
            logger.info(f"Auto-detected HR question from user {user_id}")
            await handle_hr_message(message)


def _is_hr_question(text: str) -> bool:
    """
    Detect if message is an HR-related question.
    Wrapper around utils.helpers.is_hr_question for backward compatibility.
    
    Args:
        text: User message text
    
    Returns:
        True if message appears to be HR-related
    """
    from utils.helpers import is_hr_question
    return is_hr_question(text)
