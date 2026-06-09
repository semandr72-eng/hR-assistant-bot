import asyncio
from rag.query import query_knowledge_base

async def test_rag():
    result = await query_knowledge_base('Ашан', [])
    print("RAG result for 'Ашан':")
    print(result)
    print("\n---\n")
    
    result2 = await query_knowledge_base('компания', [])
    print("RAG result for 'компания':")
    print(result2)

if __name__ == "__main__":
    asyncio.run(test_rag())
