from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    trips,
    adaptive,
    groups,
    recommendations,
    safety,
    ai_chat,
    tools
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Profiles"])
api_router.include_router(trips.router, prefix="/trips", tags=["Itinerary & Trip Planning"])
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["Real-Time Adaptive Engine & What-If Simulator"])
api_router.include_router(groups.router, prefix="/groups", tags=["Group Travel, Budgeting & Voting"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Attractions, Food & Eco-Tourism"])
api_router.include_router(safety.router, prefix="/safety", tags=["Tourist Safety & Emergency SOS"])
api_router.include_router(ai_chat.router, prefix="/ai-chat", tags=["GenAI Conversational Travel Companion"])
api_router.include_router(tools.router, prefix="/tools", tags=["Travel Tools, Smart Packing & Vision AI"])
