from fastapi import APIRouter

from apps.knowledge.api.wiki import router as wiki_router

router = APIRouter()
router.include_router(wiki_router)

__all__ = ["router"]
