# 🎓 Milliy Sertifikat Tayyorgarlik Bot

Telegram bot + Mini App — O'zbekiston **Milliy Sertifikat** imtihoniga tayyorlanish uchun **Ona tili**, **Adabiyot** va **Tarix** fanlaridan darslar, interaktiv testlar, **to'liq imtihon simulyatori** va **AI tomonidan tekshiriladigan esse mashqi**.

## ✨ Xususiyatlar

- 🤖 **Aiogram 3** asosida Telegram bot
- 🌐 **Telegram Mini App** — chiroyli web interfeys (gradient dizayn, dark/light mode)
- 📚 **3 ta fan × 7 ta sinf = 21 ta yo'nalish** (5–11 sinflar)
- 📖 Darslar bazada + **Gemini / OpenRouter** AI orqali real-time generatsiya
- 🧪 Har bir mavzu uchun **5 ta interaktiv test** (A/B/C/D variantlar)
- ⏱️ **To'liq imtihon simulyatori** — 45 ta savol, 180 daqiqa timer, haqiqiy sertifikat formati
- ✍️ **Esse mashqi** — 12 ta mavzu, AI tomonidan **12 mezon bo'yicha** rasmiy mezon asosida tekshirish
- 📊 **Shaxsiy statistika** — test/esse/imtihon natijalari tarixini saqlash
- 🏆 **Liderlar jadvali** — eng yaxshi natijalar
- 🇺🇿 To'liq o'zbek tilida

## 🆕 Eng so'nggi qo'shilganlar (v2.0)

- **Imtihon simulyatori** (`/exam`) — 45 ta savol, 180 daqiqa, 10 bo'lim, A+/A/B+/B/C sertifikat darajalari
- **Esse tekshirish** (`/essay`) — 12 ta haqiqiy sertifikat mavzusi, 12 mezon bo'yicha (publitsistik uslub, dalillar, xatboshilar, imlo, punktuatsiya, leksik xilma-xillik, va h.k.) AI baholash
- **Gemini API qo'llab-quvvatlash** — OpenRouter o'rniga yoki birgalikda (GEMINI_API_KEY)
- **Progress tracking** — `/stats` va `/top` komandalar, har bir test/esse/imtihon urinishini database ga saqlash
- **Mini App Profil** — statistika va liderlar jadvali

## 📁 Loyiha tuzilmasi

```
cert_bot/
├── main.py                          # Bot polling + web server parallel
├── config.py                        # Sozlamalar (.env dan)
├── requirements.txt                 # Python dependencies
├── .env                             # BOT_TOKEN, AI kalitlari, WEBAPP_URL
├── data/
│   ├── cert_structure.json          # 45 ta savol formati, bo'limlar, ball
│   ├── essay_rubric.json            # 12 mezon (publitsistik uslub, dalillar, ...)
│   ├── essays/essay_topics.json     # 12 ta haqiqiy esse mavzusi
│   └── question_bank.json           # 30+ namuna savol (9 bo'limda)
├── database/
│   ├── models.py                    # Schema + sample mavzular + progress tracking
│   └── crud.py                      # DB CRUD funksiyalari
├── services/
│   ├── ai_service.py                # Gemini / OpenRouter orqali dars+test
│   ├── essay_service.py             # 12 mezon bo'yicha esse tekshirish
│   ├── simulator.py                 # Imtihon generatsiyasi + ballash
│   └── curriculum.py                # 21 sinf uchun DTK mavzu nomlari
├── handlers/
│   ├── main_menu.py                 # /start
│   ├── subject.py                   # Fan tanlash
│   ├── grade.py                     # Sinf tanlash
│   ├── topic.py                     # Mavzu ko'rish + AI generatsiya
│   ├── quiz.py                      # Test state machine
│   ├── webapp.py                    # /webapp komandasi
│   ├── essay.py                     # /essay komandasi
│   ├── exam.py                      # /exam komandasi
│   └── stats.py                     # /stats, /top
├── keyboards/
│   ├── main_menu.py
│   ├── subject_menu.py
│   ├── grade_menu.py
│   ├── topic_menu.py
│   ├── quiz_keyboard.py
│   └── webapp_menu.py               # WebAppInfo tugmasi
└── webapp/
    ├── server.py                    # aiohttp app
    ├── api.py                       # JSON endpointlar
    ├── README.md                    # HTTPS/ngrok bo'yicha yo'riqnoma
    └── static/
        ├── index.html
        ├── app.js                   # SPA router + sahifalar
        ├── style.css                # Dizayn tizimi
        └── vendor/telegram-web-app.js
```

## 🚀 O'rnatish

### 1. Repositoriyani klonlash

```bash
git clone https://github.com/<username>/cert_bot.git
cd cert_bot
```

### 2. Virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini yaratish

`.env.example` dan nusxa oling va to'ldiring:

```bash
cp .env.example .env
```

```env
# Telegram bot tokeni (majburiy)
BOT_TOKEN=8674519587:AAEusMZP4P7px_-Zm3lqNSV7SP-sNWLQL-w

# Bitta AI provider tanlang:
# Variant 1: Google Gemini (tavsiya etiladi — bepul, tez)
GEMINI_API_KEY=AIzaSy...     # https://aistudio.google.com/apikey dan oling

# Variant 2: OpenRouter (zaxira)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Mini App public URL (HTTPS bo'lishi SHART)
WEBAPP_URL=https://your-tunnel.ngrok-free.app
```

### 5. Botni ishga tushirish

```bash
python main.py
```

## 📚 Bot komandalar

| Komanda | Tavsif |
|---|---|
| `/start` | Asosiy menyu |
| `/webapp` | Mini App ni ochish |
| `/essay` | Esse mavzularini ko'rsatish |
| `/exam` | Imtihon simulyatori haqida ma'lumot |
| `/stats` | Shaxsiy statistikangiz |
| `/top` | Eng yaxshi natijalar (liderlar) |

## 🌐 Mini App — HTTPS sozlash

Telegram telefon orqali faqat **HTTPS** URL larga ruxsat beradi.

### ngrok bilan (eng oson):

```bash
# 1. Bot alohida terminalda ishlab tursin
python main.py

# 2. Ikkinchi terminalda tunnel
ngrok http 8080

# 3. .env ga public URL
# WEBAPP_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

## 📡 API Endpointlar

### Mavzu va test
| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/health` | Sog'liq |
| GET | `/api/subjects` | Fanlar ro'yxati |
| GET | `/api/grades?subject=<name>` | Sinflar |
| GET | `/api/topics?grade_id=<id>` | Mavzular (auto-seed curriculum dan) |
| GET | `/api/topic/<id>` | Dars matni |
| POST | `/api/topic/<id>/generate` | AI generatsiya |
| GET | `/api/quiz/<topic_id>` | 5 ta test |
| POST | `/api/quiz/<topic_id>/submit` | Javob tekshirish (progress tracking bilan) |

### Esse
| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/essay/topics` | 12 ta esse mavzusi |
| GET | `/api/essay/topic/<id>` | Bitta mavzu (vaziyat + 2 qarash) |
| POST | `/api/essay/grade` | Esse matnini 12 mezon bo'yicha tekshirish |

### Imtihon simulyatori
| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/exam/meta` | Imtihon formati (bo'limlar, vaqt, ball) |
| GET | `/api/exam/generate?seed=...` | Yangi imtihon (45 savol) |
| POST | `/api/exam/grade` | Yopiq + esse birgalikda ballash |

### Progress tracking
| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/user/<id>/stats` | Foydalanuvchi umumiy statistikasi |
| GET | `/api/user/<id>/attempts?kind=...` | So'nggi urinishlar tarixi |
| GET | `/api/leaderboard?limit=10` | Top foydalanuvchilar |

## 🎯 Imtihon formati (haqiqiy sertifikatga mos)

| Bo'lim | Savollar | Ball/savol | Jami |
|---|---|---|---|
| Imlo qoidalari | 2 | 1.1 | 2.2 |
| Lug'at boyligi | 2 | 1.1 | 2.2 |
| Til birliklari uslubiyati | 2 | 1.1 | 2.2 |
| Grammatika | 6 | 1.1 | 6.6 |
| Punktuatsiya | 3 | 1.1 | 3.3 |
| Adabiyot nazariyasi va tarixi | 5 | 1.7 | 8.5 |
| O'qish savodxonligi | 8 | 1.7 | 13.6 |
| Mavzular doirasida moslashtirish | 3 | 2.5 | 7.5 |
| Lingvistik va badiiy tahlil | 9 | 2.5 | 22.5 |
| **Yozma savodxonlik (esse)** | 1 | 24.0 | 24.0 |
| **JAMI** | **41** | — | **92.6** |

> Eslatma: Real sertifikatda 45 ta savol. Bu loyihada 41 ta savol + 1 esse = **42 ta, 76.8 ball** (O-1 va O-2 turdagi ochiq savollar avtomatik tekshirilmaydi).

## ✍️ Esse baholash mezoni (12 ta, har biri 0–2 ball, jami 24 ball)

1. **Publitsistik uslub** — badiiy/so'zlashuvdan farqli
2. **Vaziyat yuzasidan qarashlar** — ikki qarash + shaxsiy fikr
3. **Dalillar bilan asoslash** — har bir qarash dalillangan
4. **Matn yaxlitligi** — kirish, asosiy qism, xulosa
5. **Mantiqiy qurilish + xatboshilar** — to'g'ri ajratilgan
6. **Mantiqiy-mazmuniy izchillik** — fikrlar takrori yo'q
7. **Imlo** — xatolik 0 → 2 ball
8. **Punktuatsiya** — xatolik 0 → 2 ball
9. **Qo'shimcha qo'llash** — uslubiy to'g'rilik
10. **So'z qo'llash** — o'rinli ishlatish
11. **Leksik xilma-xillik** — tasviriy vositalar
12. **Til tozaligi** — sheva/vulgarizm yo'qligi

**Diskvalifikatsiya (2 ball):** mavzuga mos emas, 100 so'zdan kam, ko'chirilgan
**0 ball:** esse yozilmagan, faqat kirish yozilgan, kirill alifbosida

## 🛠 Texnologiyalar

- **Python 3.10+**
- **aiogram 3.13+** — Telegram Bot API
- **aiosqlite** — asinxron SQLite
- **aiohttp** — Mini App HTTP server
- **Google Gemini 2.0 Flash** yoki **OpenRouter** — AI generatsiya
- **Telegram WebApp SDK** — frontend

## 📜 Litsenziya

MIT

## 🤝 Hissa qo'shish

Pull request xush kelibdi. Kattaroq o'zgarishlar uchun avval issue oching.
