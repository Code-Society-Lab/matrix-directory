from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers.auth_router import router as auth_router
from app.routers.label_router import router as labels_router
from app.routers.profile_router import (
    public_router as public_profiles_router,
    router as profile_router,
)
from app.routers.project_router import router as projects_router
from app.routers.project_type_router import router as project_types_router

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app_secret,
    session_cookie="matrix_oidc_flow",
    max_age=10 * 60,
    same_site="lax",
    https_only=settings.session_cookie_secure,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(project_types_router, prefix="/api")
app.include_router(labels_router, prefix="/api")


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


def mount_static_sites(application: FastAPI, static_directory: Path) -> None:
    """Mount the built documentation and frontend when their files exist."""
    documentation_directory = static_directory / "docs"
    frontend_index = static_directory / "index.html"
    frontend_assets = static_directory / "assets"

    if documentation_directory.is_dir():

        @application.get("/docs", include_in_schema=False)
        def documentation_root_redirect() -> RedirectResponse:
            return RedirectResponse(url="/docs/", status_code=307)

        application.mount(
            "/docs",
            StaticFiles(directory=documentation_directory, html=True),
            name="documentation",
        )

    if not frontend_index.is_file():
        return

    if frontend_assets.is_dir():
        application.mount(
            "/assets",
            StaticFiles(directory=frontend_assets),
            name="frontend-assets",
        )

    @application.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        reserved_path = path in {"api", "docs"} or path.startswith(("api/", "docs/"))
        if reserved_path:
            raise HTTPException(status_code=404, detail="Not Found")

        requested_file = (static_directory / path).resolve()
        if requested_file.is_relative_to(static_directory) and requested_file.is_file():
            return FileResponse(requested_file)

        return FileResponse(frontend_index)


mount_static_sites(app, Path(__file__).resolve().parent.parent / "static")
