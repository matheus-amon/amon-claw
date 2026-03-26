from pydantic import BaseModel, Field


class MathResult(BaseModel):
    result: float
    explication: str = Field(description='Explicação simples em pt-BR')
