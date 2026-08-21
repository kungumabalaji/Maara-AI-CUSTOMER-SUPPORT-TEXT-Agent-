from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import ChatRequest, ChatResponse, Source
from services import llm_service, rag_service

app = FastAPI(title="MAARA Support API")

# Dev-only: the Vite dev server picks an arbitrary localhost port, so any
# localhost/127.0.0.1 origin is allowed here. Lock this down before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="message must not be empty")

    try:
        results = rag_service.search(question, top_k=5)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    context_chunks = [result["content"] for result in results]

    try:
        answer = llm_service.answer_from_context(question, context_chunks)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return ChatResponse(
        answer=answer,
        sources=[Source(**result) for result in results],
    )
