"""Quiz handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.crud import get_quizzes_by_topic, get_topic_by_id
from keyboards import (
    get_quiz_keyboard,
    get_quiz_navigation_keyboard,
    get_quiz_result_keyboard,
)

router = Router()


class QuizState(StatesGroup):
    in_progress = State()


@router.callback_query(F.data.startswith("quiz_start:"))
async def cb_quiz_start(callback: CallbackQuery, state: FSMContext):
    """Start quiz"""
    parts = callback.data.split(":")
    topic_id = int(parts[1])
    question_index = int(parts[2])

    quizzes = await get_quizzes_by_topic(topic_id)
    if not quizzes:
        await callback.answer("Bu mavzu uchun testlar hali yo'q!", show_alert=True)
        return

    if question_index >= len(quizzes):
        question_index = 0

    await state.set_state(QuizState.in_progress)
    await state.update_data(
        topic_id=topic_id,
        quizzes=quizzes,
        current_index=question_index,
        score=0,
        answers={},
    )

    await show_question(callback, state)
    await callback.answer()


async def show_question(callback: CallbackQuery, state: FSMContext):
    """Display current quiz question"""
    data = await state.get_data()
    quizzes = data["quizzes"]
    current_index = data["current_index"]
    quiz = quizzes[current_index]

    options = [
        quiz["option_a"],
        quiz["option_b"],
        quiz["option_c"],
        quiz["option_d"],
    ]

    text = (
        f"🧪 <b>Test {current_index + 1}/{len(quizzes)}</b>\n\n"
        f"{quiz['question']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_quiz_keyboard(data["topic_id"], current_index, options),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("quiz_answer:"))
async def cb_quiz_answer(callback: CallbackQuery, state: FSMContext):
    """Handle quiz answer"""
    parts = callback.data.split(":")
    topic_id = int(parts[1])
    question_index = int(parts[2])
    selected_option = parts[3]

    data = await state.get_data()
    quizzes = data["quizzes"]
    quiz = quizzes[question_index]

    is_correct = selected_option == quiz["correct_option"]
    new_score = data["score"] + (1 if is_correct else 0)
    answers = data["answers"]
    answers[str(question_index)] = {
        "selected": selected_option,
        "correct": quiz["correct_option"],
        "is_correct": is_correct,
        "explanation": quiz.get("explanation", ""),
    }

    await state.update_data(score=new_score, answers=answers)

    correct_letter = quiz["correct_option"]
    correct_text = quiz[f"option_{correct_letter.lower()}"]
    result_text = (
        "✅ <b>To'g'ri!</b>"
        if is_correct
        else f"❌ <b>Noto'g'ri!</b> To'g'ri javob: {correct_letter}) {correct_text}"
    )
    if quiz.get("explanation"):
        result_text += f"\n\n💡 <i>{quiz['explanation']}</i>"

    text = (
        f"🧪 <b>Test {question_index + 1}/{len(quizzes)}</b>\n\n"
        f"{quiz['question']}\n\n"
        f"{result_text}"
    )

    # If last question, show results
    if question_index == len(quizzes) - 1:
        await show_results(callback, state)
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_navigation_keyboard(topic_id, question_index, len(quizzes)),
            parse_mode="HTML",
        )

    await callback.answer()


@router.callback_query(F.data.startswith("quiz_nav:"))
async def cb_quiz_nav(callback: CallbackQuery, state: FSMContext):
    """Navigate between quiz questions"""
    parts = callback.data.split(":")
    topic_id = int(parts[1])
    question_index = int(parts[2])

    await state.update_data(current_index=question_index)
    await show_question(callback, state)
    await callback.answer()


async def show_results(callback: CallbackQuery, state: FSMContext):
    """Show quiz results"""
    data = await state.get_data()
    quizzes = data["quizzes"]
    score = data["score"]
    total = len(quizzes)
    percentage = int((score / total) * 100) if total > 0 else 0

    topic = await get_topic_by_id(data["topic_id"])

    # Detailed results
    results_text = ""
    for i, quiz in enumerate(quizzes):
        ans = data["answers"].get(str(i), {})
        status = "✅" if ans.get("is_correct") else "❌"
        results_text += f"\n{status} Savol {i + 1}: {ans.get('selected', '-')} / {ans.get('correct', '-')}"

    text = (
        f"📊 <b>Test Natijalari</b>\n\n"
        f"Mavzu: <b>{topic['title'] if topic else 'Nomalum'}</b>\n"
        f"To'g'ri javoblar: <b>{score}/{total}</b> ({percentage}%)\n"
        f"{results_text}"
    )

    if percentage >= 80:
        text += "\n\n🎉 <b>Ajoyib natija! Siz bu mavzuni mukammal bilibsiz!</b>"
    elif percentage >= 60:
        text += "\n\n👍 <b>Yaxshi natija! Biroq ba'zi mavzularni takrorlash kerak.</b>"
    else:
        text += "\n\n📚 <b>Ko'proq o'qib, qayta urinib ko'ring.</b>"

    await callback.message.edit_text(
        text,
        reply_markup=get_quiz_result_keyboard(data["topic_id"], score, total),
        parse_mode="HTML",
    )

    await state.clear()