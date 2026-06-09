"""
RAG Query Handler.
Handles queries against the knowledge base with context-aware responses.
"""

from typing import List, Dict, Optional

from rag.index import vector_index
from services.openai_client import openai_client
from utils.logging import logger
from config import RAG_TOP_K


async def query_knowledge_base(
    query: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Query the knowledge base and generate response.
    ALWAYS uses RAG for all queries to ensure answers are based on company knowledge.
    
    This is the main response generator for the bot - all user queries are processed
    through the company knowledge base to ensure accurate, company-specific answers.
    
    Args:
        query: User's query
        conversation_history: Previous conversation messages
    
    Returns:
        Generated response based on retrieved context from company knowledge base.
        If no relevant information found in knowledge base, returns fallback message
        suggesting to contact HR department.
    """
    try:
        # ALWAYS search for relevant documents in company knowledge base
        logger.debug(f"Searching knowledge base for: {query}")
        results = vector_index.similarity_search_with_score(query, k=3)
        
        # If no results found, try with expanded query terms
        if not results:
            logger.debug("No results found, trying expanded search...")
            expanded_queries = [
                f"{query} компания",
                f"{query} организация",
                f"{query} правила",
                f"{query} процедура"
            ]
            for expanded_query in expanded_queries:
                expanded_results = vector_index.similarity_search_with_score(expanded_query, k=3)
                if expanded_results:
                    results = expanded_results
                    logger.debug(f"Found results with expanded query: {expanded_query}")
                    break
        
        # Prepare context from retrieved documents (for GPT)
        context = _prepare_context(results)
        
        # Log sources for debugging (not shown to user)
        if results:
            source_names = set(d.metadata.get('source', 'Unknown') for d, _ in results)
            logger.info(f"RAG query found {len(results)} results from: {', '.join(source_names)}")
        else:
            logger.warning("No relevant documents found in company knowledge base")
        
        # Generate response with context (no sources shown)
        response = await _generate_rag_response(
            query=query,
            context=context,
            conversation_history=conversation_history
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        # Fallback to regular GPT response with warning
        return await _fallback_response(query, conversation_history)


def _prepare_context(results: List[tuple]) -> str:
    """
    Prepare context from search results (for GPT processing).
    
    Args:
        results: List of (document, score) tuples
    
    Returns:
        Formatted context string for LLM
    """
    context_parts = []
    
    for i, (doc, score) in enumerate(results, 1):
        content = doc.page_content.strip()
        context_parts.append(f"Контекст {i}:\n{content}\n")
        
    return "\n".join(context_parts)


# Export for use in router
prepare_context = _prepare_context


async def _generate_rag_response(
    query: str,
    context: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Generate response using RAG context.
    
    Args:
        query: User's query
        context: Retrieved context from knowledge base
        conversation_history: Previous conversation
    
    Returns:
        Generated response
    """
    # First, check if context actually contains relevant information
    # by asking GPT to evaluate relevance
    relevance_check_prompt = f"""Проверь, содержит ли следующий контекст информацию для ответа на вопрос пользователя.

ВОПРОС: {query}

КОНТЕКСТ:
{context}

Ответь ТОЛЬКО "ДА" или "НЕТ" и кратко объясни почему."""

    relevance_response = await openai_client.generate_text_response([
        {"role": "system", "content": "Ты - помощник, который проверяет релевантность информации. Отвечай кратко."},
        {"role": "user", "content": relevance_check_prompt}
    ])
    
    # If relevance check suggests context is not relevant, return fallback
    if "н" in relevance_response.lower() and "да" not in relevance_response.lower():
        return "К сожалению, в предоставленном контексте нет информации по этому вопросу. Рекомендую обратиться в отдел HR вашей компании для уточнения."
    
    # Context is relevant, generate proper response
    system_prompt = f"""Ты - HR-ассистент компании Ашан с доступом к базе знаний.

ВАЖНЫЕ ПРАВИЛА:
1. ВСЕГДА ОТВЕЧАЙ НА ОСНОВЕ ПРЕДОСТАВЛЕННОГО КОНТЕКСТА ИЗ БАЗЫ ЗНАНИЙ
2. ЕСЛИ В КОНТЕКСТЕ НЕТ ИНФОРМАЦИИ - ЧЕСТНО СКАЖИ ЭТО
3. НЕ ВЫДУМЫВАЙ информацию, которой нет в контексте
4. НЕ используй свои общие знания - только контекст из базы знаний компании
5. Если не знаешь ответа - посоветуй обратиться в HR отдел
6. НЕ УПОМИНАЙ источники информации в ответе - просто дай ответ

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ КОМПАНИИ АШАН:
{context}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {query}

Если в контексте НЕТ точной информации для ответа, ответь:
"К сожалению, в предоставленном контексте нет информации по этому вопросу. Рекомендую обратиться в отдел HR вашей компании для уточнения."

Не выдумывай ответ! Ответ должен основываться ТОЛЬКО на контексте из базы знаний компании.

ВАЖНО: НЕ добавляй фразу "Источник:" или ссылки на документы в текст ответа. Просто дай чёткий и понятный ответ на вопрос."""

    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # Add conversation history if available
    if conversation_history:
        # Limit history to avoid token limits
        recent_history = conversation_history[-6:]  # Last 3 exchanges
        messages.extend(recent_history)
    
    # Add current query
    messages.append({
        "role": "user",
        "content": query
    })
    
    # Generate response
    response = await openai_client.generate_text_response(messages)
    
    return response


async def _fallback_response(
    query: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Fallback to regular GPT response when RAG fails.
    
    Args:
        query: User's query
        conversation_history: Previous conversation
    
    Returns:
        Generated response
    """
    logger.info("Using fallback response (no RAG context)")
    
    system_message = {
        "role": "system",
        "content": """Ты - личный ассистент. 
        
База знаний пока пуста или не содержит информации по этому вопросу.
Ответь на основе своих общих знаний, но предупреди пользователя, 
что это не основано на специфической базе знаний."""
    }
    
    messages = [system_message]
    
    if conversation_history:
        messages.extend(conversation_history[-6:])
    
    messages.append({
        "role": "user",
        "content": query
    })
    
    response = await openai_client.generate_text_response(messages)
    
    return f"⚠️ База знаний не содержит информации по этому вопросу.\n\n{response}"


async def add_document_to_knowledge_base(file_path: str) -> dict:
    """
    Add a document to the knowledge base.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Dictionary with status and details
    """
    try:
        from pathlib import Path
        from rag.loader import document_loader
        
        # Load document
        file_path = Path(file_path)
        documents = document_loader.load_document(file_path)
        
        # Add to index
        vector_index.add_documents(documents)
        
        logger.info(f"Added {file_path.name} to knowledge base")
        
        return {
            "success": True,
            "file": file_path.name,
            "chunks": len(documents),
            "message": f"Документ {file_path.name} успешно добавлен ({len(documents)} фрагментов)"
        }
        
    except Exception as e:
        logger.error(f"Error adding document to knowledge base: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Ошибка при добавлении документа: {e}"
        }


def get_knowledge_base_stats() -> dict:
    """
    Get statistics about the knowledge base.
    
    Returns:
        Dictionary with statistics
    """
    return vector_index.get_stats()

