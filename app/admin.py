from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.storage.db import Database


def _to_int_or_none(raw: str) -> int | None:
    value = raw.strip()
    if not value:
        return None
    return int(value)


def _build_selectors(
    source_type: str,
    item_selector: str,
    title_selector: str,
    link_selector: str,
    published_selector: str,
) -> dict | None:
    if source_type != "web":
        return None
    selectors = {
        "item_selector": item_selector.strip(),
        "title_selector": title_selector.strip(),
        "link_selector": link_selector.strip(),
        "published_selector": published_selector.strip(),
    }
    if not selectors["item_selector"] or not selectors["title_selector"] or not selectors["link_selector"]:
        raise ValueError("Web source requires item/title/link selectors")
    return selectors


def create_admin_app(db: Database) -> FastAPI:
    app = FastAPI(title="Info Aggregator Admin")
    templates = Jinja2Templates(directory=str(Path(__file__).with_name("templates")))

    @app.get("/sources", response_class=HTMLResponse)
    def list_sources(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="sources.html",
            context={"sources": db.list_sources(enabled_only=False)},
        )

    @app.get("/sources/new", response_class=HTMLResponse)
    def new_source_form(request: Request, error: str = "") -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="new_source.html",
            context={"error": error},
        )

    @app.post("/sources/new")
    def create_source(
        source_name: str = Form(...),
        source_type: str = Form(...),
        source_url: str = Form(...),
        source_enabled: str = Form("1"),
        fetch_interval_seconds: str = Form(""),
        item_selector: str = Form(""),
        title_selector: str = Form(""),
        link_selector: str = Form(""),
        published_selector: str = Form(""),
    ) -> RedirectResponse:
        try:
            selectors = _build_selectors(
                source_type=source_type,
                item_selector=item_selector,
                title_selector=title_selector,
                link_selector=link_selector,
                published_selector=published_selector,
            )
            db.add_source(
                name=source_name.strip(),
                source_type=source_type.strip(),
                url=source_url.strip(),
                enabled=source_enabled == "1",
                fetch_interval_seconds=_to_int_or_none(fetch_interval_seconds),
                selectors=selectors,
            )
        except (ValueError, TypeError):
            return RedirectResponse(url="/sources/new?error=invalid_input", status_code=303)
        return RedirectResponse(url="/sources", status_code=303)

    @app.post("/sources/{source_id}/toggle")
    def toggle_source(source_id: int, enabled: str = Form(...)) -> RedirectResponse:
        db.toggle_source(source_id, enabled == "1")
        return RedirectResponse(url="/sources", status_code=303)

    @app.post("/sources/{source_id}/delete")
    def delete_source(source_id: int) -> RedirectResponse:
        db.delete_source(source_id)
        return RedirectResponse(url="/sources", status_code=303)

    @app.get("/settings", response_class=HTMLResponse)
    def settings_form(request: Request) -> HTMLResponse:
        max_push = db.get_setting("max_push_per_cycle", "5")
        summary = db.get_setting("summary_when_exceed", "true")
        return templates.TemplateResponse(
            request=request,
            name="settings.html",
            context={
                "max_push_per_cycle": max_push,
                "summary_when_exceed": summary,
            },
        )

    @app.post("/settings")
    def save_settings(
        max_push_per_cycle: str = Form(...),
        summary_when_exceed: str = Form("true"),
    ) -> RedirectResponse:
        max_push = int(max_push_per_cycle)
        if max_push <= 0:
            raise ValueError("max_push_per_cycle must be > 0")
        db.set_setting("max_push_per_cycle", str(max_push))
        db.set_setting("summary_when_exceed", "true" if summary_when_exceed == "true" else "false")
        return RedirectResponse(url="/settings", status_code=303)

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/sources", status_code=302)

    return app
