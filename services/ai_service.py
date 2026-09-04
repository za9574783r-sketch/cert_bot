"""AI Service for generating lessons and quizzes.

Provider priority (cascading fallback):
1. ``GEMINI_API_KEY`` (Google Gemini 2.0 Flash) — preferred, fast, free tier
2. OpenRouter ``minimax/minimax-m3:free`` — secondary fallback (when
   configured by setting ``OPENROUTER_MODEL_PRIMARY`` or by default)
3. OpenRouter ``meta-llama/llama-3.1-8b-instruct:free`` — last-resort fallback

All providers expose the same payload shape: a single system + user
prompt, returning plain text. OpenRouter may wrap it in markdown code
fences, so we strip those before parsing.
"""
import json
import os
import aiohttp
import asyncio
from typing import Dict, List, Optional
from config import OPENROUTER_API_KEY, GEMINI_API_KEY

from database.crud import (
    get_topic_by_grade_and_title,
    topic_has_quizzes,
    get_topic_by_id,
    create_topic,
    create_quiz,
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Provider chain — tried in order, first success wins. Override with env
# vars like ``OPENROUTER_MODELS="model1:free,model2:free"`` if you want
# a different set. All listed models are free-tier on OpenRouter as of
# the project's initial publish.
DEFAULT_OPENROUTER_MODELS = [
    "minimax/minimax-m3:free",
    "google/gemma-4-31b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]


def _openrouter_models() -> List[str]:
    """Return the list of OpenRouter models to try, in order.

    Reads from the ``OPENROUTER_MODELS`` env var (comma-separated) when
    present, otherwise returns the default chain. Lets users add/remove
    models without touching code.
    """
    raw = os.getenv("OPENROUTER_MODELS", "").strip()
    if raw:
        return [m.strip() for m in raw.split(",") if m.strip()]
    return list(DEFAULT_OPENROUTER_MODELS)


# Backward-compat shims for any code that still references these names.
OPENROUTER_MODEL_PRIMARY = _openrouter_models()[0]
OPENROUTER_MODEL_FALLBACK = _openrouter_models()[-1]

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

SYSTEM_PROMPT_LESSON = """Sen O'zbekiston Milliy Sertifikat imtihoniga tayyorlovchi o'quvchilar uchun dars tayyorlovchi AI yordamchisisan.

Vazifa: Berilgan fan, sinf va mavzu bo'yicha 0 dan boshlab mukammal tushuntirib beradigan dars yoz.

Talablar:
1. Dars HTML formatida bo'lsin (aiogram 3 uchun: <b>, <i>, <code>, <blockquote> teglari)
2. O'zbek tilida, aniq va tushunarli tilda
3. Mavzu 0 dan mukammal darajagacha yoritilishi kerak
4. Misollar, jadvallar, sxemalar (matn ko'rinishida) ishlatilishi kerak
5. Milliy sertifikat imtihonining darajasiga mos kelishi kerak
6. Dars uzunligi 1500-3000 belgilar oralig'ida
7. Sarlavha <b> bilan ajratilgan bo'lsin

Javob faqat dars matni bo'lsin, hech qanday qo'shimcha izohsiz."""

SYSTEM_PROMPT_QUIZ = """Sen O'zbekiston Milliy Sertifikat imtihoniga tayyorlovchi o'quvchilar uchun test savollari yaratisiz.

Vazifa: Berilgan dars mavzusi bo'yicha 5 ta interaktiv test savoli yarating.

Talablar:
1. Har bir savol 4 ta variantli (A, B, C, D) bo'lsin
2. Faqat 1 ta to'g'ri javob bo'lsin
3. Savollar murakkablik darajasi o'sib borsin (1-oddiy, 5-murakkab)
4. Har bir savolga tushuntirish (explanation) qo'shilsin
5. Milliy sertifikat imtihoni formatiga mos kelishi kerak
6. Javob JSON formatida bo'lsin

JSON format:
{
  "quizzes": [
    {
      "question": "Savol matni?",
      "option_a": "Variant A",
      "option_b": "Variant B",
      "option_c": "Variant C",
      "option_d": "Variant D",
      "correct_option": "A",
      "explanation": "Nima uchun bu to'g'ri javob"
    },
    ...
  ]
}

Javob faqat JSON bo'lsin, hech qanday qo'shimcha matnsiz."""


def _provider() -> str:
    """Return the name of the active LLM provider.

    Order: Gemini → OpenRouter primary → OpenRouter fallback. Returns
    "none" when no key is configured.
    """
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        return "gemini"
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
        return "openrouter"
    return "none"


def _ai_available() -> bool:
    return _provider() != "none"


async def _call_gemini(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Call Google Gemini and return the first text candidate."""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt + "\n\n" + user_prompt}
                ],
            }
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000},
    }
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
            async with session.post(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    err = await response.text()
                    print(f"Gemini error {response.status}: {err[:200]}")
                    return None
                data = await response.json()
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


async def _call_openrouter(payload: dict) -> Optional[str]:
    """Helper to call OpenRouter chat completions"""
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
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    return content.strip() if content else None
                else:
                    error_text = await response.text()
                    print(f"OpenRouter API error: {response.status} - {error_text}")
                    return None
    except asyncio.TimeoutError:
        print("OpenRouter API timeout")
        return None
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return None


async def _call_llm(system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> Optional[str]:
    """Provider-agnostic LLM call with cascading fallbacks.

    Tries, in order:
    1. Gemini (if GEMINI_API_KEY is set)
    2. Each OpenRouter model in :func:`_openrouter_models` — first non-empty
       response wins. This lets the bot keep working when one free model
       rate-limits or is down; the next model in the chain takes over.
    """
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        out = await _call_gemini(system_prompt, user_prompt)
        if out:
            return out
        # Gemini returned nothing (rate-limit / outage) — fall through to
        # OpenRouter chain instead of giving up immediately.
        print("Gemini returned no content, falling back to OpenRouter chain")

    if not (OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here"):
        return None

    temperature = 0.5 if json_mode else 0.7
    max_tokens = 2000 if json_mode else 3000
    last_err: Optional[str] = None
    for model in _openrouter_models():
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            out = await _call_openrouter(payload)
        except Exception as e:  # defensive — _call_openrouter already swallows
            out = None
            last_err = repr(e)
        if out:
            if model != _openrouter_models()[0]:
                print(f"OpenRouter fallback succeeded with model={model}")
            return out
        print(f"OpenRouter model {model} returned no content")
    print(f"All OpenRouter models exhausted. last_err={last_err}")
    return None


async def generate_lesson(subject: str, grade: int, topic_title: str) -> Optional[str]:
    """Generate lesson content via the active LLM provider."""
    if not _ai_available():
        return None

    user_prompt = f"""
Fan: {subject}
Sinf: {grade}-sinf
Mavzu: {topic_title}

Ushbu mavzu bo'yicha Milliy Sertifikat imtihoniga tayyorlovchi {grade}-sinf o'quvchisi uchun 0 dan mukammal darajagacha tushuntiruvchi dars yozing.
"""
    return await _call_llm(SYSTEM_PROMPT_LESSON, user_prompt)


async def generate_quizzes(lesson_content: str, topic_title: str) -> Optional[List[Dict]]:
    """Generate 5 quiz questions via the active LLM provider."""
    if not _ai_available():
        return None

    user_prompt = f"""
Dars mavzusi: {topic_title}

Dars mazmuni:
{lesson_content[:2000]}

Ushbu dars bo'yicha 5 ta test savoli yarating.
"""
    content = await _call_llm(SYSTEM_PROMPT_QUIZ, user_prompt, json_mode=True)
    if not content:
        return None

    # Strip code fences if present
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        result = json.loads(content)
        return result.get("quizzes", [])
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None


async def _save_quizzes(topic_id: int, quizzes: List[Dict]) -> int:
    """Save generated quizzes, return count saved"""
    saved = 0
    for i, q in enumerate(quizzes):
        try:
            await create_quiz(
                topic_id,
                q["question"],
                q["option_a"],
                q["option_b"],
                q["option_c"],
                q["option_d"],
                q["correct_option"],
                q.get("explanation", ""),
                i + 1,
            )
            saved += 1
        except Exception as e:
            print(f"Error saving quiz {i}: {e}")
    return saved


async def get_or_generate_lesson(
    grade_id: int,
    topic_title: str,
    subject_name: str,
    grade_num: int,
) -> Dict:
    """Get lesson from DB or generate via AI.
    Returns: {"topic": dict|None, "generated": bool}
    """
    # 1) Mavjudligini tekshiramiz
    existing = await get_topic_by_grade_and_title(grade_id, topic_title)
    if existing:
        if await topic_has_quizzes(existing["id"]):
            return {"topic": existing, "generated": False}

        # Mavjud topic, lekin testlari yo'q — testlarni generatsiya qilamiz
        quizzes = await generate_quizzes(existing["content"], topic_title)
        if quizzes:
            await _save_quizzes(existing["id"], quizzes)
        return {"topic": existing, "generated": False}

    # 2) Topic yo'q — yangi dars generatsiya qilamiz
    if not _ai_available():
        return {"topic": None, "generated": False}

    lesson_content = await generate_lesson(subject_name, grade_num, topic_title)
    if not lesson_content:
        return {"topic": None, "generated": False}

    new_topic_id = await create_topic(
        grade_id=grade_id,
        title=topic_title,
        content=lesson_content,
        order_num=0,
        is_ai_generated=True,
    )

    quizzes = await generate_quizzes(lesson_content, topic_title)
    if quizzes:
        await _save_quizzes(new_topic_id, quizzes)

    new_topic = await get_topic_by_id(new_topic_id)
    return {"topic": new_topic, "generated": True}