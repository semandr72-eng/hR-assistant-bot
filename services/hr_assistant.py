"""
HR Assistant Client.
Specialized client for HR-related operations.
"""

from typing import List, Dict, Optional
from services.openai_client import openai_client
from utils.logging import logger


class HRAssistantClient:
    """HR-specific assistant with specialized capabilities."""
    
    def __init__(self):
        """Initialize HR assistant with system prompt."""
        self.system_prompt = """Ты - профессиональный HR-ассистент с экспертизой в области подбора персонала, оценки кандидатов и HR-аналитики.

ТВОИ ОСНОВНЫЕ ФУНКЦИИ:

1. **Анализ резюме:**
   - Оценка соответствия кандидата вакансии
   - Выявление сильных и слабых сторон
   - Рекомендации по улучшению резюме
   - Проверка на пробелы в опыте

2. **Подготовка к собеседованию:**
   - Генерация вопросов для интервью
   - Оценка ответов кандидата
   - Советы по проведению собеседования
   - Составление оценочных листов

3. **HR-консультации:**
   - Ответы на вопросы по трудовому законодательству
   - Рекомендации по мотивации и удержанию
   - Советы по адаптации сотрудников
   - Помощь в составлении должностных инструкций

4. **Анализ рынка труда:**
   - Рекомендации по зарплатным ожиданиям
   - Анализ конкурентов
   - Тренды в подборе персонала

ВАЖНЫЕ ПРАВИЛА:
- Отвечай профессионально, но дружелюбно
- Используй структуру и списки для удобства
- Дай конкретные рекомендации, а не общие фразы
- Указывай, когда нужна дополнительная информация
- Сохраняй конфиденциальность данных кандидатов
- Отвечай на русском языке"""

    async def analyze_resume(
        self,
        resume_text: str,
        job_description: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Analyze a resume and provide feedback.
        
        Args:
            resume_text: Resume content
            job_description: Optional job description for matching
            history: Conversation history
        
        Returns:
            Analysis results
        """
        try:
            logger.info("Analyzing resume")
            
            prompt = f"""Проанализируй следующее резюме:

{resume_text}

{'\n\nТребования к вакансии:\n' + job_description if job_description else ''}

Дай структурированный анализ:
1. Общее впечатление (кратко)
2. Сильные стороны кандидата
3. Зоны роста / вопросы для собеседования
4. Соответствие вакансии (если указано)
5. Рекомендации по улучшению резюме"""

            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-4:])
            messages.append({"role": "user", "content": prompt})
            
            response = await openai_client.generate_text_response(messages)
            
            return {
                "analysis": response,
                "type": "resume_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            raise
    
    async def generate_interview_questions(
        self,
        job_description: str,
        seniority: str = "middle",
        num_questions: int = 10,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Generate interview questions for a position.
        
        Args:
            job_description: Job description
            seniority: Junior/Middle/Senior
            num_questions: Number of questions
            history: Conversation history
        
        Returns:
            Interview questions
        """
        try:
            logger.info(f"Generating {num_questions} interview questions for {seniority} level")
            
            prompt = f"""Составь список вопросов для собеседования на позицию.

Описание вакансии:
{job_description}

Уровень: {seniority}
Количество вопросов: {num_questions}

Структурируй вопросы по категориям:
1. Общие вопросы о кандидате
2. Профессиональные компетенции
3. Технические навыки (если применимо)
4. Мягкие навыки и командная работа
5. Ситуационные вопросы
6. Вопросы о мотивации и карьерных целях

Для каждого вопроса уеди, что оцениваем."""

            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-4:])
            messages.append({"role": "user", "content": prompt})
            
            response = await openai_client.generate_text_response(messages)
            
            return {
                "questions": response,
                "type": "interview_questions"
            }
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            raise
    
    async def evaluate_candidate_answer(
        self,
        question: str,
        candidate_answer: str,
        job_description: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Evaluate a candidate's answer to an interview question.
        
        Args:
            question: Interview question
            candidate_answer: Candidate's response
            job_description: Job description for context
            history: Conversation history
        
        Returns:
            Evaluation with score and feedback
        """
        try:
            logger.info("Evaluating candidate answer")
            
            prompt = f"""Оцени ответ кандидата на собеседовании.

Вопрос: {question}
Ответ кандидата: {candidate_answer}
{'\n\nОписание вакансии:\n' + job_description if job_description else ''}

Дай оценку:
1. Оценка по шкале 1-10
2. Сильные стороны ответа
3. Слабые стороны / что можно улучшить
4. Соответствие требованиям вакансии
5. Рекомендации: стоит ли продолжать собеседование"""

            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-4:])
            messages.append({"role": "user", "content": prompt})
            
            response = await openai_client.generate_text_response(messages)
            
            return {
                "evaluation": response,
                "type": "answer_evaluation"
            }
            
        except Exception as e:
            logger.error(f"Error evaluating candidate answer: {e}")
            raise
    
    async def hr_consultation(
        self,
        query: str,
        context: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Provide HR consultation on various topics.
        
        Args:
            query: HR-related question
            context: Additional context
            history: Conversation history
        
        Returns:
            Consultation response
        """
        try:
            logger.info(f"HR consultation request: {query[:50]}...")
            
            prompt = f"""Вопрос по HR: {query}
{'\n\nДополнительный контекст:\n' + context if context else ''}

Дай профессиональный совет с учетом:
- Трудового законодательства РФ
- Лучших практик
- Конкретных шагов для решения проблемы"""

            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-4:])
            messages.append({"role": "user", "content": prompt})
            
            response = await openai_client.generate_text_response(messages)
            
            return {
                "consultation": response,
                "type": "hr_consultation"
            }
            
        except Exception as e:
            logger.error(f"Error in HR consultation: {e}")
            raise
    
    async def create_job_description(
        self,
        position: str,
        requirements: List[str],
        company_info: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Create a professional job description.
        
        Args:
            position: Position title
            requirements: List of requirements
            company_info: Company information
            history: Conversation history
        
        Returns:
            Job description
        """
        try:
            logger.info(f"Creating job description for {position}")
            
            prompt = f"""Создай профессиональное описание вакансии.

Должность: {position}
Требования:
{chr(10).join(f'• {req}' for req in requirements)}
{'\n\nО компании:\n' + company_info if company_info else ''}

Структура описания:
1. Заголовок с названием должности
2. Краткое описание компании (если предоставлено)
3. Описание роли и задач
4. Требования к кандидату
5. Будет преимуществом
6. Условия работы и benefits
7. Призыв к действию

Сделай описание привлекательным для кандидатов."""

            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-4:])
            messages.append({"role": "user", "content": prompt})
            
            response = await openai_client.generate_text_response(messages)
            
            return {
                "job_description": response,
                "type": "job_description"
            }
            
        except Exception as e:
            logger.error(f"Error creating job description: {e}")
            raise


# Global HR assistant client instance
hr_assistant = HRAssistantClient()
