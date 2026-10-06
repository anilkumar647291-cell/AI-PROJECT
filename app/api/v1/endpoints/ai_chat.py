from fastapi import APIRouter
from app.schemas.tools import AIChatRequest, AIChatResponse
from app.services.ai_assistant_service import AIAssistantService

router = APIRouter()

@router.post("/message", response_model=AIChatResponse)
def converse_with_ai_companion(req: AIChatRequest):
    """
    Conversational GenAI Travel Companion:
    Provides context-aware natural language trip explanations, dynamic replanning advice,
    and cultural etiquette guidance.
    """
    return AIAssistantService.answer_travel_query(req)
