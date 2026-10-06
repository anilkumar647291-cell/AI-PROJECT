from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.tools import (
    SmartPackingRequest,
    SmartPackingResponse,
    LandmarkRecognitionResponse,
    TranslationRequest,
    TranslationResponse
)
from app.services.ai_assistant_service import AIAssistantService
from app.services.vision_service import VisionService

router = APIRouter()

@router.post("/smart-packing", response_model=SmartPackingResponse)
def get_smart_packing_list(req: SmartPackingRequest):
    """
    AI Smart Packing Advisor:
    Generates a personalized packing checklist considering destination climate,
    duration, planned activities, and demographic needs (senior, kids, solo).
    """
    return AIAssistantService.generate_smart_packing(req)

@router.post("/landmark-recognition", response_model=LandmarkRecognitionResponse)
async def recognize_landmark_image(
    file: Optional[UploadFile] = File(None),
    landmark_hint: Optional[str] = Form(None)
):
    """
    Computer Vision Landmark Recognition:
    Processes traveler-submitted photos or landmark hints to identify historic monuments,
    generating historical context, architectural style, visiting advice, and audio guide script.
    """
    filename = file.filename if file else ""
    return VisionService.recognize_landmark(filename=filename, landmark_hint=landmark_hint)

@router.post("/translate", response_model=TranslationResponse)
def translate_tourism_phrase(req: TranslationRequest):
    """
    Multilingual & Voice Travel Assistant:
    Translates essential tourist requests with phonetic pronunciations and cultural etiquette tips.
    """
    return AIAssistantService.translate_phrase(req)
