"""Database schema and initialization"""
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bot.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    icon TEXT DEFAULT '📚',
    order_num INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    grade_num INTEGER NOT NULL,
    display_name TEXT NOT NULL,
    order_num INTEGER DEFAULT 0,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(subject_id, grade_num)
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    order_num INTEGER DEFAULT 0,
    is_ai_generated INTEGER DEFAULT 0,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    order_num INTEGER DEFAULT 0,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_grades_subject ON grades(subject_id);
CREATE INDEX IF NOT EXISTS idx_topics_grade ON topics(grade_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_topic ON quizzes(topic_id);

-- User progress: each Telegram user has a row of accumulated statistics
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_active_at TEXT NOT NULL DEFAULT (datetime('now')),
    quizzes_taken INTEGER NOT NULL DEFAULT 0,
    quizzes_correct INTEGER NOT NULL DEFAULT 0,
    essays_graded INTEGER NOT NULL DEFAULT 0,
    essays_total_score REAL NOT NULL DEFAULT 0,
    exams_taken INTEGER NOT NULL DEFAULT 0,
    exams_total_score REAL NOT NULL DEFAULT 0,
    exams_max_score REAL NOT NULL DEFAULT 0
);

-- Per-attempt records: every quiz/essay/exam submission is stored here
-- so users can see their history and we can compute aggregates.
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('quiz', 'essay', 'exam')),
    ref_id INTEGER,
    payload TEXT NOT NULL,            -- JSON: questions snapshot, essay text, etc.
    score REAL NOT NULL DEFAULT 0,    -- 0..max_score
    max_score REAL NOT NULL DEFAULT 0,
    percentage REAL NOT NULL DEFAULT 0,
    level TEXT,                       -- A+, A, B+, B, C, etc.
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_kind ON attempts(kind);
CREATE INDEX IF NOT EXISTS idx_attempts_created ON attempts(created_at);
"""

# Sample data — barcha matnlar Python tomonidan kiritiladi (apostroflar xavfsiz)
SUBJECTS = [
    (1, "native_language", "Ona tili", "🇺🇿", 1),
    (2, "literature", "Adabiyot", "📖", 2),
    (3, "history", "Tarix", "🏛️", 3),
]

GRADES = [
    # (id, subject_id, grade_num, display_name, order_num)
    (1, 1, 5, "5-sinf", 1), (2, 1, 6, "6-sinf", 2), (3, 1, 7, "7-sinf", 3),
    (4, 1, 8, "8-sinf", 4), (5, 1, 9, "9-sinf", 5), (6, 1, 10, "10-sinf", 6), (7, 1, 11, "11-sinf", 7),
    (8, 2, 5, "5-sinf", 1), (9, 2, 6, "6-sinf", 2), (10, 2, 7, "7-sinf", 3),
    (11, 2, 8, "8-sinf", 4), (12, 2, 9, "9-sinf", 5), (13, 2, 10, "10-sinf", 6), (14, 2, 11, "11-sinf", 7),
    (15, 3, 5, "5-sinf", 1), (16, 3, 6, "6-sinf", 2), (17, 3, 7, "7-sinf", 3),
    (18, 3, 8, "8-sinf", 4), (19, 3, 9, "9-sinf", 5), (20, 3, 10, "10-sinf", 6), (21, 3, 11, "11-sinf", 7),
]

TOPICS = [
    # 5-sinf Ona tili (grade_id=1)
    (1, 1, "Unlilar va undoshlar", """📝 <b>Unlilar va undoshlar</b>

Unlilar — ovozi ochiq, tovush yuragi bo'lib o'tadigan harflardir. O'zbek tilida 6 ta unli bor: <b>a, o, u, e, i, o'</b>.

Undoshlar — ovozi to'q, tovush yo'li cheklangan harflardir. Ular shakllanishi va ovozi bo'yicha turli guruhlarga bo'linadi.

<b>Unlilar xususiyatlari:</b>
• O'zbek tilida unlilar so'z boshida, o'rtasida va oxirida bo'lishi mumkin
• Unlilar emas, undoshlar so'z tuzilmasining asosini tashkil etadi
• Har bir so'zda kamida bitta unli bo'lishi shart

<b>Undoshlar turlari:</b>
1. <b>Sokin undoshlar:</b> p, t, k, q, s, sh, f, x, h
2. <b>Jahriy undoshlar:</b> b, d, g, j, z, v, y, l, m, n, r
3. <b>Yorqin undoshlar:</b> ch, ts

<b>Misol:</b> So'z "kitob" da: k (undosh), i (unli), t (undosh), o (unli), b (undosh).""", 1),

    (2, 1, "So'z turlari", """📝 <b>So'z turlari</b>

O'zbek tilida so'zlar ma'nosi va grammatik xususiyatlari bo'yicha quyidagi turlarga bo'linadi:

1. <b>Ot (Noun)</b> — obyekt, shaxs, hodisa, sifat va h.k. ni ifodalaydi. Masalan: <i>kitob, o'qituvchi, yomg'ir, go'zal</i>

2. <b>Fe'l (Verb)</b> — harakat, holat, voqea ni ifodalaydi. Masalan: <i>o'qiydi, yozmoqda, keldi, bo'ladi</i>

3. <b>Sifat (Adjective)</b> — obyektning xususiyat, rangi, o'lchami va h.k. ni ifodalaydi. Masalan: <i>katta, kichik, qizil, tez</i>

4. <b>Ravish (Adverb)</b> — harakatning usuli, vaqti, joyi, darajasi ni ifodalaydi. Masalan: <i>tez, yorqin, bugun, u yerda</i>

5. <b>Son (Numeral)</b> — son miqdorini yoki tartib raqamini ifodalaydi. Masalan: <i>bir, ikki, uch, birinchi, ikkinchi</i>

6. <b>O'rnlik (Pronoun)</b> — so'z o'rnini bosadi. Masalan: <i>men, sen, u, bu, shu</i>

7. <b>Bog'lovchi (Conjunction)</b> — so'zlar yoki gaplarni bog'laydi. Masalan: <i>va, ammo, lekin, yoki</i>

8. <b>Yuklama (Particle)</b> — ma'no qismini kuchaytiradi. Masalan: <i>ham, hamda, -chi, -mi</i>

9. <b>Undov (Interjection)</b> — his-tuyg'ularni ifodalaydi. Masalan: <i>oy, vah, bravo, afsus</i>""", 2),

    (3, 1, "Gap tuzilishi", """📝 <b>Gap tuzilishi</b>

O'zbek tilida gap quyidagi elementlardan iborat bo'ladi:

<b>Asosiy a'zolar:</b>
• <b>Ega (Subject)</b> — kim? nima? (ot yoki o'rnlik)
• <b>Kesim (Predicate)</b> — nima qiladi? qanday? (fe'l)

<b>Qo'shimcha a'zolar:</b>
• <b>To'ldiruvchi (Object)</b> — kimni? nimani? (ot kelishig'ida)
• <b>Aniqlovchi (Attribute)</b> — qanday? qaysi? (sifat)
• <b>Hol (Adverbial modifier)</b> — qayerda? qachon? qanday? (ravish)

<b>Gap tartibi (SOV):</b>
O'zbek tilida oddiy gap tartibi: <b>Ega + To'ldiruvchi + Kesim</b>

<b>Misollar:</b>
• <i>Men kitob o'qiyman.</i> (Men — ega, kitob — to'ldiruvchi, o'qiyman — kesim)
• <i>Bolalar sinfga keldi.</i> (Bolalar — ega, sinfga — hol, keldi — kesim)
• <i>U go'zal gul sotib oldi.</i> (U — ega, go'zal gul — to'ldiruvchi, sotib oldi — kesim)""", 3),

    # 5-sinf Adabiyot (grade_id=8)
    (4, 8, "O'zbek xalq ertaklari", """📖 <b>O'zbek xalq ertaklari</b>

Xalq ertaklari — xalq ogzaki ijodi janrlaridan biri bo'lib, u ijodiy tasavvur, hayol kuchi va milliy qadriyatlarning aksidir.

<b>Ertak turlari:</b>
1. <b>Sehrli ertaklar</b> — sehrli, ajoyib voqealar, jin, pari, devlar ishtirok etadi. Masalan: <i>"Zumrad va Qimmat", "Yigitali kuchli"</i>
2. <b>Hayotiy (maishiy) ertaklar</b> — odamlar hayoti, mehnat, adolat haqida. Masalan: <i>"Nasriddin afandi" haqidagi ertaklar</i>
3. <b>Hayvonlar haqidagi ertaklar</b> — hayvonlar shaxs sifatida ishtirok etadi. Masalan: <i>"Tulki va Qarg'a", "Bo'ri bilan Quyon"</i>

<b>Xususiyatlari:</b>
• "Bir bor ekan, bir yo'q ekan" bilan boshlanadi
• Yaxshi yomonni yengadi, adolat g'alaba qozonadi
• Xalq tilida, sodda va tushunarli tilda yozilgan""", 1),

    (5, 8, "Alisher Navoiy hayoti va ijodi", """📖 <b>Alisher Navoiy (1441-1501)</b>

<b>Hayoti:</b>
Alisher Navoiy — o'zbek adabiyotining buyuk shoiri, davlat arbobi va hayriyachi. 1441-yilda Hirota tug'ilgan. Husayn Boyqaro saroyida vazir lavozimida ishlagan.

<b>Asarlari:</b>
1. <b>"Xamsa" (Besh asar)</b> — "Hayrat ul-abror", "Farhad va Shirin", "Layli va Majnun", "Sab'ai sayyor", "Saddi Iskandariy"
2. <b>"Lison ut-Tayr"</b> — didaktik asar
3. <b>"Muhakamat al-Lughatayn"</b> — tilshunoslik asari
4. <b>"Majolis un-Nafois"</b> — shoirlar tazkirasi
5. <b>Devonlari</b> — gazallar, ruboiylar, qit'alar to'plami

<b>Merosi:</b>
Navoiy o'zbek tilini rasmiy davlat tili maqomiga ko'tardi, adabiy tilni shakllantirdi. Uning asarlari bugungi kunda ham o'qiladi va o'rganiladi.""", 2),

    # 5-sinf Tarix (grade_id=15)
    (6, 15, "O'zbekiston tarixi: qadimgi davr", """🏛️ <b>O'zbekiston tarixi: qadimgi davr</b>

<b>Qadimgi davr (I ming yillik avvalgi yarmi — VII asr)</b>

Markaziy Osiyo — dunyodagi eng qadimiy sivilizatsiyalar vatanidan biri. Bu yerda odam hayoti ming yillar avval paydo bo'lgan.

<b>1. Ilk davlatlar:</b>
• Baqtriya, Sug'diyona, Xorazm — qadimgi davlatlar
• Dehiston, Afrosiyob — yirik shaharlar
• Hunlar, Kangarlar — ko'chmanqi qabilalar

<b>2. Amir Temur davri (XIV-XV asrlar):</b>
• 1370-yilda Amir Temur mamlakatni birlashtirdi
• Samarqand — poytaxt qilindi
• Ilmiy, madaniy, me'morchilik yutuqlari
• "Temur tuzuklari" — qonunchilik asari

<b>3. Shayboniylar davri (XVI asr):</b>
• Shayboniyxon — Movarounnahrda davlat qurdi
• Buxoro — poytaxt
• Madaniyat va ilm rivojlandi

<b>Asosiy yutuqlar:</b>
• Me'morchilik: Registon, Bibixonim, Guri Amir
• Ilm: Ulug'bek rasadxonasi, astronomiya
• Adabiyot: Navoiy, Jomiy, Bobur""", 1),
]

QUIZZES = [
    # topic 1 — Unlilar va undoshlar
    (1, "O'zbek tilida nechta unli bor?", "4 ta", "6 ta", "8 ta", "10 ta", "B", "O'zbek tilida 6 ta unli bor: a, o, u, e, i, o'", 1),
    (1, "Quyidagilardan qaysi biri soqin (sokin) undosh?", "b", "d", "k", "g", "C", "k — soqin undosh, boshqalar jahriy undoshlar", 2),
    (1, "So'z 'olma' da nechta unli bor?", "1 ta", "2 ta", "3 ta", "4 ta", "B", "o va a — 2 ta unli", 3),
    (1, "Unlilar so'zda qanday vazifani bajaradi?", "So'z tuzilmasining asosini tashkil etadi", "So'zni o'qish imkonini beradi", "Undoshlar o'rnini bosadi", "Ma'no bermaydi", "B", "Unlilar bo'lmasa so'zni o'qib bo'lmaydi", 4),
    (1, "Qaysi harf \"o'\" unlisini ifodalaydi?", "o", "ó", "o'", "ö", "C", "O'zbek alifbosida o' harfi maxsus unli", 5),

    # topic 2 — So'z turlari
    (2, "Harakatni ifodalovchi so'z turi qaysi?", "Ot", "Fe'l", "Sifat", "Ravish", "B", "Fe'l — harakatni ifodalaydi", 1),
    (2, "Quyidagilardan qaysi biri ravish?", "kitob", "o'qiydi", "tez", "go'zal", "C", "tez — harakat usulini ifodalaydi (ravish)", 2),
    (2, "Sifat so'z turining misoli:", "kelmoqda", "katta", "va", "oy", "B", "katta — obyekt xususiyatini ifodalaydi", 3),
    (2, "Son so'z turining misoli qaysi?", "birinchi", "kelish", "qizil", "yaxshi", "A", "birinchi — tartib soni", 4),
    (2, "Bog'lovchi so'z turining vazifasi nima?", "Harakat bildiradi", "So'zlarni bog'laydi", "Obyekt bildiradi", "His bildiradi", "B", "Bog'lovchi so'zlar va gaplarni bog'laydi", 5),
]


async def _seed_data(db: aiosqlite.Connection) -> None:
    """Insert sample data using parameterized queries."""
    await db.executemany(
        "INSERT OR IGNORE INTO subjects (id, name, display_name, icon, order_num) VALUES (?, ?, ?, ?, ?)",
        SUBJECTS,
    )

    await db.executemany(
        "INSERT OR IGNORE INTO grades (id, subject_id, grade_num, display_name, order_num) VALUES (?, ?, ?, ?, ?)",
        GRADES,
    )

    await db.executemany(
        "INSERT OR IGNORE INTO topics (id, grade_id, title, content, order_num) VALUES (?, ?, ?, ?, ?)",
        TOPICS,
    )

    await db.executemany(
        """INSERT OR IGNORE INTO quizzes
           (topic_id, question, option_a, option_b, option_c, option_d, correct_option, explanation, order_num)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        QUIZZES,
    )


async def init_db() -> None:
    """Initialize database with schema and sample data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await _seed_data(db)
        await db.commit()

    print(f"Database initialized at {DB_PATH}")