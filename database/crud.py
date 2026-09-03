"""Database CRUD operations"""
import aiosqlite
from typing import List, Optional, Dict, Any
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bot.db"


def _new_connection():
    """Return a context manager for a new sqlite connection.
    Use: `async with _new_connection() as db: ...`
    """
    return aiosqlite.connect(DB_PATH)


# Subjects
async def get_subjects() -> List[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM subjects ORDER BY order_num") as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def get_subject_by_name(name: str) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM subjects WHERE name = ?", (name,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_subject_by_id(subject_id: int) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


# Grades
async def get_grades_by_subject(subject_id: int) -> List[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM grades WHERE subject_id = ? ORDER BY order_num",
            (subject_id,),
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def get_grade_by_id(grade_id: int) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM grades WHERE id = ?", (grade_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


# Topics
async def get_topics_by_grade(grade_id: int) -> List[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM topics WHERE grade_id = ? ORDER BY order_num, id",
            (grade_id,),
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def get_topic_by_id(topic_id: int) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_topic_by_grade_and_title(grade_id: int, title: str) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM topics WHERE grade_id = ? AND title = ?",
            (grade_id, title),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_topic(
    grade_id: int,
    title: str,
    content: str,
    order_num: int = 0,
    is_ai_generated: bool = False,
) -> int:
    async with _new_connection() as db:
        cursor = await db.execute(
            "INSERT INTO topics (grade_id, title, content, order_num, is_ai_generated) "
            "VALUES (?, ?, ?, ?, ?)",
            (grade_id, title, content, order_num, 1 if is_ai_generated else 0),
        )
        await db.commit()
        return cursor.lastrowid


# Quizzes
async def get_quizzes_by_topic(topic_id: int) -> List[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM quizzes WHERE topic_id = ? ORDER BY order_num, id",
            (topic_id,),
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def create_quiz(
    topic_id: int,
    question: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_option: str,
    explanation: str = "",
    order_num: int = 0,
) -> int:
    async with _new_connection() as db:
        cursor = await db.execute(
            """INSERT INTO quizzes
               (topic_id, question, option_a, option_b, option_c, option_d,
                correct_option, explanation, order_num)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                topic_id, question, option_a, option_b, option_c, option_d,
                correct_option, explanation, order_num,
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def topic_has_quizzes(topic_id: int) -> bool:
    async with _new_connection() as db:
        async with db.execute(
            "SELECT COUNT(*) FROM quizzes WHERE topic_id = ?",
            (topic_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0] > 0)


async def topic_exists(topic_id: int) -> bool:
    async with _new_connection() as db:
        async with db.execute("SELECT 1 FROM topics WHERE id = ?", (topic_id,)) as cursor:
            return await cursor.fetchone() is not None