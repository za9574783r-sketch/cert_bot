# Milliy Sertifikat Mini App

Telegram Mini App — `cert_bot` ning web frontend qismi. Aiogram bot inline
tugmalari bilan birga ishlaydi.

## Arxitektura

```
cert_bot/
├── main.py                    # bot polling + aiohttp web server parallel
├── config.py                  # WEBAPP_HOST/PORT/URL
├── handlers/webapp.py         # /webapp komandasi
├── keyboards/webapp_menu.py   # WebAppInfo tugmasi
└── webapp/
    ├── server.py              # aiohttp app
    ├── api.py                 # JSON endpointlar
    └── static/
        ├── index.html         # SPA shell
        ├── app.js             # router + sahifalar
        ├── style.css          # dizayn tizimi
        └── vendor/telegram-web-app.js
```

## API endpointlar

| Method | Path | Maqsad |
|---|---|---|
| GET | `/api/health` | sog'liq tekshiruvi |
| GET | `/api/subjects` | 3 ta fan |
| GET | `/api/grades?subject=<name>` | Fan uchun sinflar |
| GET | `/api/topics?grade_id=<id>` | Mavzular (bo'sh bo'lsa curriculum dan seed) |
| GET | `/api/topic/<id>` | Dars matni |
| POST | `/api/topic/<id>/generate` | AI generatsiya |
| GET | `/api/quiz/<topic_id>` | 5 ta test |
| POST | `/api/quiz/<topic_id>/submit` | Javob tekshirish |

## HTTPS — Telegram talabi

Telegram telefondan `http://` URL larga ruxsat bermaydi. HTTPS kerak.

#### Variant A: ngrok (eng oson)

```bash
# 1. ngrok o'rnatish (https://ngrok.com dan)
# 2. Bot ishga tushirish
python main.py

# 3. Alohida terminalda tunnel ochish
ngrok http 8080

# 4. .env ga public URL ni qo'yish
# WEBAPP_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app

# 5. BotFather ga o'tish
#    /mybots → @ai_academic_bot → Bot Settings → Menu Button
#    URL: https://xxxx-xx-xx-xx.ngrok-free.app
#    Text: 🚀 Mini App ochish
```

#### Variant B: cloudflared (tez, bepul)

```bash
cloudflared tunnel --url http://localhost:8080
# HTTPS URL beradi, .env ga qo'ying
```

#### Variant C: real domen

Server yoki VPS'ga deploy qiling, Nginx + Let's Encrypt bilan HTTPS sozlang.

## Botdagi integratsiya

Bot 2 ta usulda Mini App ni ochadi:

1. **`/start`** xabariga qo'shilgan reply keyboard
2. **`/webapp`** komandasi

Ikkalasi ham `keyboards/webapp_menu.get_webapp_keyboard()` dan foydalanadi.

## Curriculum seed

`services/curriculum.py` 21 sinf uchun (3 fan × 7 sinf) real DTK
mavzu nomlarini saqlaydi. Bo'sh sinfga `GET /api/topics` chaqiruvi shu
nomlarni bazaga kiritadi (bo'sh `content` bilan). Keyin foydalanuvchi
mavzuni ochganda `POST /api/topic/<id>/generate` AI ga dars yaratadi.

## OPENROUTER_API_KEY

`.env` ga haqiqiy OpenRouter API kalitini qo'ying. Bo'sh bo'lsa AI
generatsiya ishlamaydi, lekin mavzu nomlari va tayyor darslar ko'rinadi.