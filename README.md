# 🎓 Milliy Sertifikat Tayyorgarlik Bot

Telegram bot + Mini App — O'zbekiston Milliy Sertifikat imtihoniga tayyorlanish uchun **Ona tili**, **Adabiyot** va **Tarix** fanlaridan darslar va interaktiv testlar.

## ✨ Xususiyatlar

- 🤖 **Aiogram 3** asosida Telegram bot
- 🌐 **Telegram Mini App** — chiroyli web interfeys (gradient dizayn, dark/light mode)
- 📚 **3 ta fan × 7 ta sinf = 21 ta yo'nalish**
- 📖 Darslar bazada + **OpenRouter** AI orqali real-time generatsiya
- 🧪 Har bir mavzu uchun **5 ta interaktiv test** (A/B/C/D variantlar bilan)
- 📊 Batafsil natija va tushuntirishlar
- 🇺🇿 To'liq o'zbek tilida

## 📁 Loyiha tuzilmasi

```
cert_bot/
├── main.py                 # Bot polling + web server parallel
├── config.py               # Sozlamalar (.env dan)
├── requirements.txt        # Python dependencies
├── .env                    # BOT_TOKEN, OPENROUTER_API_KEY, WEBAPP_URL
├── database/
│   ├── models.py          # Schema + sample mavzular
│   └── crud.py            # DB CRUD funksiyalari
├── services/
│   ├── ai_service.py      # OpenRouter orqali dars+test generatsiya
│   └── curriculum.py      # 21 sinf uchun real DTK mavzu nomlari
├── handlers/
│   ├── main_menu.py       # /start
│   ├── subject.py         # Fan tanlash
│   ├── grade.py           # Sinf tanlash
│   ├── topic.py           # Mavzu ko'rish + AI generatsiya
│   ├── quiz.py            # Test state machine
│   └── webapp.py          # /webapp komandasi
├── keyboards/
│   ├── main_menu.py
│   ├── subject_menu.py
│   ├── grade_menu.py
│   ├── topic_menu.py
│   ├── quiz_keyboard.py
│   └── webapp_menu.py     # WebAppInfo tugmasi
└── webapp/
    ├── server.py          # aiohttp app
    ├── api.py             # JSON endpointlar
    ├── README.md         # HTTPS/ngrok bo'yicha yo'riqnoma
    └── static/
        ├── index.html
        ├── app.js         # SPA router + sahifalar
        ├── style.css      # Dizayn tizimi
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
BOT_TOKEN=8674519587:AAEusMZP4P7px_-Zm3lqNSV7SP-sNWLQL-w
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
WEBAPP_URL=https://your-tunnel.ngrok-free.app
```

### 5. Botni ishga tushirish

```bash
python main.py
```

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

# 4. BotFather → /mybots → @ai_academic_bot → Menu Button → URL
```

Batafsil: [`webapp/README.md`](webapp/README.md)

## 📡 API Endpointlar

| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/health` | Sog'liq |
| GET | `/api/subjects` | Fanlar ro'yxati |
| GET | `/api/grades?subject=<name>` | Sinflar |
| GET | `/api/topics?grade_id=<id>` | Mavzular (auto-seed curriculum dan) |
| GET | `/api/topic/<id>` | Dars matni |
| POST | `/api/topic/<id>/generate` | AI generatsiya |
| GET | `/api/quiz/<topic_id>` | 5 ta test |
| POST | `/api/quiz/<topic_id>/submit` | Javob tekshirish |

## 🛠 Texnologiyalar

- **Python 3.10+**
- **aiogram 3.13+** — Telegram Bot API
- **aiosqlite** — asinxron SQLite
- **aiohttp** — Mini App HTTP server (FastAPI kerak emas)
- **OpenRouter** — AI dars va test generatsiya
- **Telegram WebApp SDK** — frontend

## 📜 Litsenziya

MIT

## 🤝 Hissa qo'shish

Pull request xush kelibdi. Kattaroq o'zgarishlar uchun avval issue oching.