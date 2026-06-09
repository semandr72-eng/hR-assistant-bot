import asyncio
from rag.query import query_knowledge_base

async def test_rag():
    result = await query_knowledge_base('название компании Ашан', [])
    print("RAG result for 'название компании Ашан':")
    print(result)
    print("\n---\n")
    
    result2 = await query_knowledge_base('как называется компания', [])
    print("RAG result for 'как называется компания':")
    print(result2)

if __name__ == "__main__":
    asyncio.run(test_rag())
