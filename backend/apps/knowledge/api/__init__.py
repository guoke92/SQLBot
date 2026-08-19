from fastapi import APIRouter

from apps.knowledge.semantic.api import router as semantic_router

router = APIRouter()
router.include_router(semantic_router)

__all__ = ["router"]
