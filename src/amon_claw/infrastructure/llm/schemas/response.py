from pydantic import BaseModel, Field


class MathResult(BaseModel):
    result: float | None
    explication: str = Field(description='Simple explication in pt-BR')


class GenericOutput(BaseModel):
    greeting: str = Field(..., description='A brief greeting in pt-BR')
    response: str
    useful_question: str = Field(
        ..., description='a pertinent question to keep the conversation active'
    )


class AgentOutput(BaseModel):
    ai_answer: MathResult | GenericOutput
