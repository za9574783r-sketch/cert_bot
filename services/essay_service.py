"""Essay grading service.

Grades student essays against the official Milliy Sertifikat rubric
(`data/essay_rubric.json`). Uses an LLM (Gemini by default; OpenRouter
fallback) to score each of the 12 criteria, then aggregates to a
0..24 final score with explicit disqualification handling.

All API calls are best-effort and timeout-bounded — a failure returns
``None`` so the caller can present a "manual review required" state.
"""
from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from config import OPENROUTER_API_KEY, GEMINI_API_KEY


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

RUBRIC_PATH = Path(__file__).parent.parent / "data" / "essay_rubric.json"
TOPICS_PATH = Path(__file__).parent.parent / "data" / "essays" / "essay_topics.json"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CriterionResult:
    criterion_id: int
    name: str
    score: float
    justification: str


@dataclass
class EssayGrade:
    topic_id: int
    topic_title: str
    word_count: int
    total_score: float
    max_score: int
    percentage: float
    level: str
    level_comment: str
    criteria: List[CriterionResult]
    disqualification_reason: Optional[str]
    feedback_summary: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_rubric() -> Dict[str, Any]:
    with open(RUBRIC_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_topics() -> List[Dict[str, Any]]:
    with open(TOPICS_PATH, encoding="utf-8") as f:
        return json.load(f)["topics"]


def get_topic(topic_id: int) -> Optional[Dict[str, Any]]:
    for t in _load_topics():
        if t["id"] == topic_id:
            return t
    return None


def list_topics() -> List[Dict[str, Any]]:
    return _load_topics()


def count_words(text: str) -> int:
    """Approximate Uzbek word count — split on whitespace + punctuation."""
    cleaned = re.sub(r"[\s,.;:!?\"'()«»—\-]+", " ", text).strip()
    return len([w for w in cleaned.split() if w])


# ---------------------------------------------------------------------------
# LLM callers
# ---------------------------------------------------------------------------

def _provider() -> str:
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        return "gemini"
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
        return "openrouter"
    return "none"


def _build_grading_prompt(essay: str, topic: Dict[str, Any], rubric: Dict[str, Any]) -> str:
    """Build the system prompt that asks the LLM to score all 12 criteria."""
    criteria_lines = []
    for c in rubric["criteria"]:
        scoring = " | ".join(f"{k} ball: {v}" for k, v in c["scoring"].items())
        criteria_lines.append(
            f"{c['id']}. {c['name']} (max {c['max_score']} ball): {scoring}"
        )
    criteria_block = "\n".join(criteria_lines)

    disqual = "\n".join(f"- {c}" for c in rubric["disqualification_conditions"])

    return f"""Sen O'zbekiston Milliy Sertifikat imtihoni bo'yicha yuqori malakali ekspert — ona tili va adabiyot o'qituvchisisan.

VAZIYA (mavzu):
{topic['title']}
{topic['situation']}

QARASH A: {topic['viewpoint_a']}
QARASH B: {topic['viewpoint_b']}

TALABGORNING ESSE MATNI:
\"\"\"{essay}\"\"\" ESSE MATNI TUGADI.

SENING VAZIFANG:
Quyidagi 12 mezon bo'yicha esseni baholash. Har bir mezon uchun ball va qisqa asoslash ber.

MEZONLAR (jami {rubric['total_score']} ball):
{criteria_block}

DISKVALIFIKATSIYA SHARTLARI (agar birortasi bajarilsa — jami 2 yoki 0 ball):
{disqual}

JAVOB FORMATI — FAQAT JSON:
{{
  "disqualification": null yoki sabab matni,
  "criteria": [
    {{"id": 1, "score": <0|0.5|1|1.5|2>, "justification": "<1-2 gap asoslash>"}},
    ... (12 ta)
  ],
  "feedback_summary": "<3-4 gapli umumiy xulosa>"
}}

MUHIM:
- Faqat JSON qaytar, qo'shimcha izohsiz.
- Har bir mezon uchun ruxsat etilgan ballardan birini tanla: 0, 0.5, 1, 1.5, yoki 2.
- Diskvalifikatsiya bo'lsa, criteria bo'sh massiv bo'lishi mumkin.
"""


async def _call_gemini(prompt: str) -> Optional[str]:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
            async with session.post(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=90)
            ) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    print(f"Gemini error: {resp.status} - {err[:200]}")
                    return None
                data = await resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
                return text.strip() if text else None
    except asyncio.TimeoutError:
        print("Gemini timeout")
        return None
    except Exception as e:
        print(f"Gemini exception: {e}")
        return None


async def _call_openrouter(prompt: str) -> Optional[str]:
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/cert_bot",
        "X-Title": "Milliy Sertifikat Bot",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPENROUTER_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=90),
            ) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    print(f"OpenRouter error: {resp.status} - {err[:200]}")
                    return None
                data = await resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or None
    except Exception as e:
        print(f"OpenRouter exception: {e}")
        return None


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _parse_llm_response(raw: str) -> Dict[str, Any]:
    """Extract a JSON object from the LLM's response, tolerating noise."""
    text = _strip_code_fence(raw)
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find the first {...} block
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError("LLM response did not contain a parseable JSON object")


# ---------------------------------------------------------------------------
# Main grading entry point
# ---------------------------------------------------------------------------

async def grade_essay(topic_id: int, essay_text: str) -> Optional[EssayGrade]:
    """Grade an essay asynchronously.

    Returns ``None`` if the LLM is unavailable or fails — caller should fall
    back to a "manual review" message.
    """
    topic = get_topic(topic_id)
    if not topic:
        return None

    rubric = _load_rubric()
    word_count = count_words(essay_text)

    provider = _provider()
    if provider == "none":
        return None

    prompt = _build_grading_prompt(essay_text, topic, rubric)

    raw = await (_call_gemini(prompt) if provider == "gemini" else _call_openrouter(prompt))
    if not raw:
        return None

    try:
        parsed = _parse_llm_response(raw)
    except ValueError as e:
        print(f"Parse error: {e}; raw={raw[:300]}")
        return None

    # Disqualification branch
    disqual = parsed.get("disqualification")
    if disqual and isinstance(disqual, str) and disqual.strip():
        score = 0 if "0 ball" in disqual or "yozilmagan" in disqual.lower() else 2
        return EssayGrade(
            topic_id=topic_id,
            topic_title=topic["title"],
            word_count=word_count,
            total_score=float(score),
            max_score=rubric["total_score"],
            percentage=round((score / rubric["total_score"]) * 100, 1),
            level="Disqualification" if score == 0 else "Past",
            level_comment=disqual,
            criteria=[],
            disqualification_reason=disqual,
            feedback_summary=parsed.get("feedback_summary", "Diskvalifikatsiya qo'llanildi."),
        )

    # Normal branch — sum criteria scores
    criteria_results: List[CriterionResult] = []
    by_id = {c["id"]: c for c in rubric["criteria"]}
    for item in parsed.get("criteria", []):
        cid = int(item.get("id", 0))
        score = float(item.get("score", 0))
        # Clamp to valid range
        score = max(0.0, min(2.0, score))
        # Snap to half-points
        score = round(score * 2) / 2
        cdef = by_id.get(cid, {"name": f"Criterion {cid}", "max_score": 2})
        criteria_results.append(
            CriterionResult(
                criterion_id=cid,
                name=cdef["name"],
                score=score,
                justification=str(item.get("justification", ""))[:500],
            )
        )

    total = sum(c.score for c in criteria_results)
    percentage = round((total / rubric["total_score"]) * 100, 1)
    level, comment = _level_for(percentage)

    return EssayGrade(
        topic_id=topic_id,
        topic_title=topic["title"],
        word_count=word_count,
        total_score=round(total, 1),
        max_score=rubric["total_score"],
        percentage=percentage,
        level=level,
        level_comment=comment,
        criteria=criteria_results,
        disqualification_reason=None,
        feedback_summary=parsed.get("feedback_summary", ""),
    )


def _level_for(percentage: float) -> tuple[str, str]:
    if percentage >= 86:
        return "A+", "A'lo daraja — oliy o'quv yurtiga kirish uchun tavsiya etiladi"
    if percentage >= 71:
        return "A", "A'lo — bilim mustahkam"
    if percentage >= 56:
        return "B+", "Yaxshi — ba'zi mavzularni takrorlash tavsiya etiladi"
    if percentage >= 41:
        return "B", "Qoniqarli — tizimli o'qish kerak"
    return "C", "Qoniqarsiz — qayta tayyorlanish tavsiya etiladi"


# ---------------------------------------------------------------------------
# Serialization helper for the API layer
# ---------------------------------------------------------------------------

def grade_to_dict(grade: EssayGrade) -> Dict[str, Any]:
    return {
        "topic_id": grade.topic_id,
        "topic_title": grade.topic_title,
        "word_count": grade.word_count,
        "total_score": grade.total_score,
        "max_score": grade.max_score,
        "percentage": grade.percentage,
        "level": grade.level,
        "level_comment": grade.level_comment,
        "disqualification_reason": grade.disqualification_reason,
        "feedback_summary": grade.feedback_summary,
        "criteria": [asdict(c) for c in grade.criteria],
    }
