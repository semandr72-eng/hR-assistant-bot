"""
Tests for HR Assistant functionality.
"""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Set mock environment variables before importing modules
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_key'
os.environ['USE_PROXYAPI'] = 'false'

from services.hr_assistant import HRAssistantClient, hr_assistant


class TestHRQuestionDetection:
    """Tests for HR question auto-detection."""
    
    def test_hr_keywords_positive(self):
        """Test positive HR question detection."""
        from utils.helpers import is_hr_question
        
        # Test key HR keywords
        assert is_hr_question("отпуск")
        assert is_hr_question("зарплата")
        assert is_hr_question("график работы")
        assert is_hr_question("онбординг")
        assert is_hr_question("руководитель")
        assert is_hr_question("как оформить")
        assert is_hr_question("больничный")
        assert is_hr_question("премия")
        assert is_hr_question("обучение")
        assert is_hr_question("карьера")
        assert is_hr_question("правила")
        assert is_hr_question("документ")
        assert is_hr_question("справка")

    def test_hr_keywords_negative(self):
        """Test non-HR question detection."""
        from utils.helpers import is_hr_question
        
        non_hr_questions = [
            "Привет, как дела?",
            "Какое сегодня число?",
            "Погода хорошая",
            "Расскажи анекдот",
            "Нарисуй кота"
        ]

        for question in non_hr_questions:
            assert not is_hr_question(question), f"Ложное срабатывание: {question}"
    
    def test_hr_keywords_case_insensitive(self):
        """Test case-insensitive detection."""
        from utils.helpers import is_hr_question
        
        assert is_hr_question("КАК ОФОРМИТЬ ОТПУСК?")
        assert is_hr_question("Как ОФОРМИТЬ отпуск")
        assert is_hr_question("отпуск")


class TestHRAssistantClient:
    """Tests for HR Assistant client."""
    
    @pytest.fixture
    def hr_client(self):
        """Create HR assistant client instance."""
        return HRAssistantClient()
    
    def test_initialization(self, hr_client):
        """Test client initialization."""
        assert hr_client.system_prompt is not None
        assert "HR-ассистент" in hr_client.system_prompt
    
    @pytest.mark.asyncio
    async def test_analyze_resume(self, hr_client):
        """Test resume analysis."""
        with patch('services.hr_assistant.openai_client') as mock_client:
            mock_client.generate_text_response = AsyncMock(
                return_value="Анализ резюме"
            )
            
            result = await hr_client.analyze_resume(
                resume_text="Опыт работы: 5 лет",
                job_description="Требования: 3+ года"
            )
            
            assert result["type"] == "resume_analysis"
            assert "Анализ резюме" in result["analysis"]
    
    @pytest.mark.asyncio
    async def test_generate_interview_questions(self, hr_client):
        """Test interview questions generation."""
        with patch('services.hr_assistant.openai_client') as mock_client:
            mock_client.generate_text_response = AsyncMock(
                return_value="1. Общие вопросы\n2. Профессиональные вопросы"
            )
            
            result = await hr_client.generate_interview_questions(
                job_description="Разработчик Python",
                seniority="middle",
                num_questions=10
            )
            
            assert result["type"] == "interview_questions"
            assert "Общие вопросы" in result["questions"]
    
    @pytest.mark.asyncio
    async def test_hr_consultation(self, hr_client):
        """Test HR consultation."""
        with patch('services.hr_assistant.openai_client') as mock_client:
            mock_client.generate_text_response = AsyncMock(
                return_value="Рекомендация по оформлению отпуска"
            )
            
            result = await hr_client.hr_consultation(
                query="Как оформить отпуск?",
                context="Полный год работы"
            )
            
            assert result["type"] == "hr_consultation"
            assert "Рекомендация" in result["consultation"]


class TestHRAssistantIntegration:
    """Integration tests for HR assistant."""
    
    @pytest.mark.asyncio
    async def test_hr_consultation_with_context(self):
        """Test HR consultation with context."""
        with patch('services.hr_assistant.openai_client') as mock_client:
            mock_client.generate_text_response = AsyncMock(
                return_value="Рекомендация по оформлению отпуска 28 дней"
            )
            
            result = await hr_assistant.hr_consultation(
                query="Сколько дней отпуска?",
                context="Правила компании: отпуск 28 дней"
            )
            
            assert result["type"] == "hr_consultation"
            assert "28 дней" in result["consultation"]


@pytest.mark.asyncio
async def test_hr_assistant_global_instance():
    """Test global HR assistant instance."""
    assert hr_assistant is not None
    assert isinstance(hr_assistant, HRAssistantClient)
