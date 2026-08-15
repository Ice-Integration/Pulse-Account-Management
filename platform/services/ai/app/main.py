import os
import re
from typing import Any

import asyncpg
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pgvector.asyncpg import register_vector
from pydantic import BaseModel

app = FastAPI(title="Pulse AI Support", version="1.0.0")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pulse:pulse@localhost:5432/pulse")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini")
EMBED_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

BLOCKED = [r"ignore (all|previous) instructions", r"reveal .*system prompt", r"developer message", r"bypass .*policy"]

class AskRequest(BaseModel):
    question: str
    account_id: str | None = None

@app.get('/health')
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai"}

async def retrieve(question: str, limit: int = 5) -> list[dict[str, Any]]:
    embedding = (await client.embeddings.create(model=EMBED_MODEL, input=question)).data[0].embedding
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await register_vector(conn)
        rows = await conn.fetch("SELECT id,title,content,metadata,1-(embedding <=> $1::vector) score FROM knowledge_documents WHERE embedding IS NOT NULL ORDER BY embedding <=> $1::vector LIMIT $2", embedding, limit)
        if not rows:
            rows = await conn.fetch("SELECT id,title,content,metadata,0.0 score FROM knowledge_documents WHERE content ILIKE '%' || $1 || '%' LIMIT $2", question.split()[0], limit)
        return [dict(r) for r in rows]
    finally:
        await conn.close()

@app.post('/support/ask')
async def ask(request: AskRequest) -> dict[str, Any]:
    q = request.question.strip()
    if len(q) < 3:
        raise HTTPException(400, 'question_too_short')
    if any(re.search(pattern, q, re.I) for pattern in BLOCKED):
        raise HTTPException(400, 'unsafe_prompt')
    docs = await retrieve(q)
    context = '\n\n'.join(f"SOURCE {i+1}: {d['title']}\n{d['content']}" for i, d in enumerate(docs))
    response = await client.responses.create(
        model=CHAT_MODEL,
        input=[
            {"role":"system","content":"You are Pulse Support. Answer only from supplied sources. Never invent account facts. If sources are insufficient, say so. Cite sources as [1], [2]."},
            {"role":"user","content":f"Question: {q}\n\nSources:\n{context}"},
        ],
    )
    return {"answer": response.output_text, "citations": [{"id": str(d['id']), "title": d['title'], "score": float(d['score'])} for d in docs]}
