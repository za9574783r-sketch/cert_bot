"""Handlers package initialization"""
from .main_menu import router as main_menu_router
from .subject import router as subject_router
from .grade import router as grade_router
from .topic import router as topic_router
from .quiz import router as quiz_router
from .webapp import router as webapp_router

__all__ = [
    "main_menu_router",
    "subject_router",
    "grade_router",
    "topic_router",
    "quiz_router",
    "webapp_router",
]