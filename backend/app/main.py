from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.project_routers import router as projects_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/api")


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


frontend_directory = Path(__file__).resolve().parent.parent / "static"
frontend_index = frontend_directory / "index.html"
frontend_assets = frontend_directory / "assets"

if frontend_index.is_file():
    if frontend_assets.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=frontend_assets),
            name="frontend-assets",
        )

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        requested_file = (frontend_directory / path).resolve()
        if (
            requested_file.is_relative_to(frontend_directory)
            and requested_file.is_file()
        ):
            return FileResponse(requested_file)

        return FileResponse(frontend_index)
