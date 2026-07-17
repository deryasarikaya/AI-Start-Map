from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import router, templates


app = FastAPI(title="AI Start Map")
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)
app.include_router(router)


@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    _exception: StarletteHTTPException,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=404,
    )
