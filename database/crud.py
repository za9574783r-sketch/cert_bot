"""Database CRUD operations"""
import aiosqlite
import json
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


# ---------------------------------------------------------------------------
# User stats & attempts — progress tracking
# ---------------------------------------------------------------------------

async def touch_user(user_id: int, username: str = "", full_name: str = "") -> None:
    """Insert or update a user_stats row. Called on every interaction."""
    async with _new_connection() as db:
        await db.execute(
            """INSERT INTO user_stats (user_id, username, full_name)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   username = COALESCE(NULLIF(excluded.username, ''), username),
                   full_name = COALESCE(NULLIF(excluded.full_name, ''), full_name),
                   last_active_at = datetime('now')""",
            (user_id, username, full_name),
        )
        await db.commit()


async def get_user_stats(user_id: int) -> Optional[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def record_attempt(
    user_id: int,
    kind: str,
    payload: Dict[str, Any],
    score: float,
    max_score: float,
    level: str = "",
    ref_id: Optional[int] = None,
) -> int:
    """Insert a row into attempts; returns the new attempt id."""
    if kind not in ("quiz", "essay", "exam"):
        raise ValueError(f"invalid kind: {kind}")
    percentage = round((score / max_score) * 100, 1) if max_score else 0.0
    payload_json = json.dumps(payload, ensure_ascii=False, default=str)

    async with _new_connection() as db:
        cursor = await db.execute(
            """INSERT INTO attempts
               (user_id, kind, ref_id, payload, score, max_score, percentage, level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, kind, ref_id, payload_json, score, max_score, percentage, level),
        )
        await db.commit()
        return cursor.lastrowid


async def update_user_aggregates(
    user_id: int,
    *,
    quizzes_taken: int = 0,
    quizzes_correct: int = 0,
    essays_graded: int = 0,
    essays_total_score: float = 0,
    exams_taken: int = 0,
    exams_total_score: float = 0,
    exams_max_score: float = 0,
) -> None:
    """Increment aggregate counters on user_stats."""
    async with _new_connection() as db:
        await db.execute(
            """UPDATE user_stats SET
                quizzes_taken = quizzes_taken + ?,
                quizzes_correct = quizzes_correct + ?,
                essays_graded = essays_graded + ?,
                essays_total_score = essays_total_score + ?,
                exams_taken = exams_taken + ?,
                exams_total_score = exams_total_score + ?,
                exams_max_score = exams_max_score + ?,
                last_active_at = datetime('now')
               WHERE user_id = ?""",
            (quizzes_taken, quizzes_correct, essays_graded, essays_total_score,
             exams_taken, exams_total_score, exams_max_score, user_id),
        )
        await db.commit()


async def list_user_attempts(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT id, kind, ref_id, score, max_score, percentage, level, created_at
               FROM attempts WHERE user_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Leaderboard: highest average exam percentage (with at least 1 attempt)."""
    async with _new_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT u.user_id, u.full_name, u.username,
                      u.exams_taken, u.exams_total_score, u.exams_max_score,
                      CASE WHEN u.exams_max_score > 0
                           THEN ROUND((u.exams_total_score / u.exams_max_score) * 100, 1)
                           ELSE 0 END AS avg_pct
               FROM user_stats u
               WHERE u.exams_taken > 0
               ORDER BY avg_pct DESC
               LIMIT ?""",
            (limit,),
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def count_attempts(user_id: int, kind: str) -> int:
    async with _new_connection() as db:
        async with db.execute(
            "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND kind = ?",
            (user_id, kind),
        ) as cursor:
            row = await cursor.fetchone()
            return (row[0] or 0) if row else 0