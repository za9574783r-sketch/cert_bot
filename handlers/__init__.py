"""Handlers package initialization"""
from .main_menu import router as main_menu_router
from .subject import router as subject_router
from .grade import router as grade_router
from .topic import router as topic_router
from .quiz import router as quiz_router
from .webapp import router as webapp_router
from .essay import router as essay_router
from .exam import router as exam_router
from .stats import router as stats_router
from .help_cmd import router as help_router

__all__ = [
    "main_menu_router",
    "subject_router",
    "grade_router",
    "topic_router",
    "quiz_router",
    "webapp_router",
    "essay_router",
    "exam_router",
    "stats_router",
    "help_router",
]