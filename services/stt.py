"""
Speech-to-Text Service.
Handles voice message transcription.
"""

from pathlib import Path
from typing import Union

from services.openai_client import openai_client
from utils.logging import logger


async def transcribe_voice_message(audio_path: Union[str, Path]) -> str:
    """
    Transcribe a voice message to text.
    
    Args:
        audio_path: Path to audio file (OGG, WAV, MP3, etc.)
    
    Returns:
        Transcribed text
    """
    audio_path = Path(audio_path)
    
    try:
        # OpenAI Whisper supports OGG, WAV, MP3, and other formats directly
        # No conversion needed!
        logger.debug(f"Transcribing audio: {audio_path}")
        
        # Transcribe using OpenAI Whisper
        text = await openai_client.transcribe_audio(audio_path)
        
        logger.info(f"Transcription completed: {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"Error in voice transcription: {e}")
        raise
        
