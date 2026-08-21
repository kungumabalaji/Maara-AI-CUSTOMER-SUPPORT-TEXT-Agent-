from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    row_id: int
    score: float
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
