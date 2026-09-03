import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Web server / Mini App settings
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
WEBAPP_URL = os.getenv("WEBAPP_URL", f"http://localhost:{WEBAPP_PORT}")
WEBAPP_BUTTON_TEXT = os.getenv("WEBAPP_BUTTON_TEXT", "🚀 Mini App ochish")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
    print("Warning: OPENROUTER_API_KEY not set. AI generation will not work.")

if WEBAPP_URL.startswith("http://") and WEBAPP_URL not in (
    f"http://localhost:{WEBAPP_PORT}",
    f"http://127.0.0.1:{WEBAPP_PORT}",
):
    print(
        "Warning: WEBAPP_URL is not HTTPS. Telegram Mini App requires HTTPS "
        "when opened from a phone. Use ngrok/cloudflared or set WEBAPP_URL "
        "to your public HTTPS URL."
    )