from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import user_router, health_router, article_router
from utils.exception_handlers import register_exception_handlers

app = FastAPI(
    title="FastAPI Scaffold",
    description="A FastAPI scaffold project with SQLAlchemy, Redis, and more",
    version="0.1.0"
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(article_router)


@app.get("/")
async def root():
    return {"msg": "Hello FastAPI Scaffold"}
