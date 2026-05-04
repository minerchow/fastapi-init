from .user import router as user_router
from .health import router as health_router
from .article import router as article_router

__all__ = ["user_router", "health_router", "article_router"]
