"""Full Milliy Sertifikat exam simulator.

Reproduces the official 45-question, 180-minute format from
`data/cert_structure.json`. Each ``generate_exam()`` call deterministically
picks questions per section so that the same exam structure can be re-run
for practice.

The simulator doesn't actually grade open-ended (O-1, O-2) items — those
require a teacher. For the bot, O-1 items are returned as self-check
prompts and O-2 (the essay) goes through ``essay_service.grade_essay``.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import essay_service

STRUCTURE_PATH = Path(__file__).parent.parent / "data" / "cert_structure.json"
QUESTION_BANK_PATH = Path(__file__).parent.parent / "data" / "question_bank.json"
QUESTION_BANK_EXTRA_PATH = Path(__file__).parent.parent / "data" / "question_bank_extra.json"


def _load_structure() -> Dict[str, Any]:
    with open(STRUCTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_bank() -> Dict[str, Any]:
    """Load and merge the main and extra question banks.

    The extra bank augments (does not replace) the main bank. Per-section
    question counts grow so simulators have more variety.
    """
    bank: Dict[str, list] = {}
    for path in (QUESTION_BANK_PATH, QUESTION_BANK_EXTRA_PATH):
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for section, questions in data.items():
            if section.startswith("_"):
                continue
            bank.setdefault(section, []).extend(questions)
    return bank


def get_exam_meta() -> Dict[str, Any]:
    """Return exam metadata: section breakdown, durations, scoring."""
    s = _load_structure()
    return {
        "subject": s["subject"],
        "total_questions": s["total_questions"],
        "duration_minutes": s["duration_minutes"],
        "total_score": s["total_score"],
        "sections": s["sections"],
        "passing_levels": s["passing_levels"],
    }


def generate_exam(seed: Optional[str] = None) -> Dict[str, Any]:
    """Build an exam attempt with one question per slot.

    If a real question bank is missing, fall back to a synthetic placeholder
    so the UI is still usable (the user will see "AI generatsiya" prompts).
    """
    structure = _load_structure()
    bank = _load_bank()
    rng = random.Random(seed or "default")

    questions: List[Dict[str, Any]] = []
    qid = 0
    for section in structure["sections"]:
        bank_key = section["name"]
        candidates = bank.get(bank_key, [])
        for slot in range(section["question_count"]):
            qid += 1
            if candidates:
                q = rng.choice(candidates)
                questions.append({
                    "id": qid,
                    "section_id": section["id"],
                    "section_name": bank_key,
                    "type": section["types"][0],
                    "points": section["points_per_question"],
                    "question": q.get("question", ""),
                    "options": q.get("options"),
                    "correct": q.get("correct"),
                })
            else:
                questions.append({
                    "id": qid,
                    "section_id": section["id"],
                    "section_name": bank_key,
                    "type": section["types"][0],
                    "points": section["points_per_question"],
                    "question": (
                        f"[{bank_key}] — demo savol. Bu yerda haqiqiy savol "
                        "ko'rsatiladi. AI dars generatsiyasi orqali haqiqiy "
                        "test savolini yaratish mumkin."
                    ),
                    "options": ["A) variant 1", "B) variant 2", "C) variant 3", "D) variant 4"]
                    if "Y-1" in section["types"] else None,
                    "correct": None,
                })
    return {
        "total_questions": qid,
        "duration_minutes": structure["duration_minutes"],
        "total_score": structure["total_score"],
        "questions": questions,
    }


def score_closed_questions(questions: List[Dict[str, Any]], answers: Dict[int, str]) -> Dict[str, Any]:
    """Score Y-1 / Y-2 type questions; ignore O-1 / O-2."""
    total = 0.0
    earned = 0.0
    per_question = []
    for q in questions:
        if q["type"] in ("O-1", "O-2"):
            continue
        total += q["points"]
        selected = answers.get(q["id"], "")
        correct = q.get("correct")
        is_correct = bool(correct) and selected == correct
        if is_correct:
            earned += q["points"]
        per_question.append({
            "id": q["id"],
            "is_correct": is_correct,
            "selected": selected,
            "correct": correct,
            "points_earned": q["points"] if is_correct else 0,
            "points_possible": q["points"],
        })
    return {
        "closed_score": round(earned, 2),
        "closed_max": round(total, 2),
        "per_question": per_question,
    }


async def grade_full_exam(questions: List[Dict[str, Any]],
                          closed_answers: Dict[int, str],
                          essay_topic_id: Optional[int] = None,
                          essay_text: Optional[str] = None) -> Dict[str, Any]:
    """Score a full exam: closed questions + optional essay.

    Essay grading is async because it calls an LLM. Open-ended (O-1) items
    are returned as ``null`` score for self-check — they need a teacher.
    """
    closed = score_closed_questions(questions, closed_answers)
    structure = _load_structure()
    essay_max = next(
        (s["points_per_question"] for s in structure["sections"] if "Yozma" in s["name"]),
        24.0,
    )
    total_max = structure["total_score"]

    essay_score = None
    essay_detail: Optional[Dict[str, Any]] = None
    if essay_topic_id is not None and essay_text:
        grade = await essay_service.grade_essay(essay_topic_id, essay_text)
        if grade is not None:
            essay_score = grade.total_score
            essay_detail = essay_service.grade_to_dict(grade)

    combined_earned = closed["closed_score"] + (essay_score or 0)
    percentage = round((combined_earned / total_max) * 100, 1) if total_max else 0
    level = _cert_level(percentage)

    return {
        "closed": closed,
        "essay": essay_detail,
        "essay_score": essay_score,
        "essay_max": essay_max,
        "total_earned": round(combined_earned, 2),
        "total_max": total_max,
        "percentage": percentage,
        "level": level,
    }


def _cert_level(percentage: float) -> Dict[str, str]:
    s = _load_structure()
    levels = s["passing_levels"]
    for key, info in levels.items():
        if percentage >= info["min_percent"]:
            return {"code": key, "label": info["label"], "comment": info["comment"]}
    return {"code": "C", "label": "C (Qoniqarsiz)", "comment": "Sertifikat berilmaydi"}
