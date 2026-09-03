"""aiohttp app factory for the Telegram Mini App.

Registers JSON API routes and serves the static SPA from `webapp/static/`.
Falls back to index.html for any unknown path so that deep links
(e.g. `#/topic/12`) load the SPA correctly.
"""
from pathlib import Path

from aiohttp import web

from . import api

STATIC_DIR = Path(__file__).parent / "static"


def build_app() -> web.Application:
    """Build and return the aiohttp Application."""
    app = web.Application()

    # API routes
    app.router.add_get("/api/health", api.healthcheck)
    app.router.add_get("/api/subjects", api.subjects)
    app.router.add_get("/api/grades", api.grades)
    app.router.add_get("/api/topics", api.topics)
    app.router.add_get("/api/topic/{id:\\d+}", api.topic_detail)
    app.router.add_post("/api/topic/{id:\\d+}/generate", api.topic_generate)
    app.router.add_get("/api/quiz/{topic_id:\\d+}", api.quiz_list)
    app.router.add_post("/api/quiz/{topic_id:\\d+}/submit", api.quiz_submit)

    # Static files (CSS, JS, images, vendor libs)
    app.router.add_static("/static/", path=str(STATIC_DIR), show_index=False)

    # SPA entry point
    async def index(request: web.Request) -> web.Response:
        html_path = STATIC_DIR / "index.html"
        return web.Response(
            body=html_path.read_text(encoding="utf-8"),
            content_type="text/html",
            charset="utf-8",
        )

    app.router.add_get("/", index)
    # SPA fallback — any non-/api GET path returns index.html
    app.router.add_get("/{tail:.*}", index)

    return app