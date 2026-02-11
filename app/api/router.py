from fastapi import APIRouter

from app.api import auth, categories, expenses, friends, groups

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(friends.router)
api_router.include_router(categories.router)
api_router.include_router(groups.router)
api_router.include_router(expenses.router)
