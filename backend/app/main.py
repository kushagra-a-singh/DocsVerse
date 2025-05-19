import logging
import os

import uvicorn
from app import models
from app.config import settings
from app.database import init_db
from app.models.document import Base
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

load_dotenv()


def create_app():
    """Factory function to create FastAPI app"""
    app = FastAPI(
        title="DocsVerse Document Research Chatbot API",
        description="API for document ingestion, querying, theming, and chat.",
        version="0.1.0",
    )

    init_db()

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger = logging.getLogger("uvicorn.error")
        logger.error(f"Validation error: {exc.errors()} | Body: {await request.body()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "body": (await request.body()).decode("utf-8"),
            },
        )

    from app.api.document import router as document_router
    from app.api.query import router as query_router
    from app.api.theme import router as theme_router

    app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
    app.include_router(query_router, prefix="/api/queries", tags=["Queries"])
    app.include_router(theme_router, prefix="/api/themes", tags=["Themes"])

    return app


app = create_app()


def verify_database():
    """Verify database connection and create tables if needed"""
    from app.database import engine

    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        from sqlalchemy import text

        with engine.connect() as conn:
            tables = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
            print(f"Tables in database: {', '.join([t[0] for t in tables])}")
    except Exception as e:
        print(f"Error verifying database: {str(e)}")
        raise


verify_database()


def verify_routes(app: FastAPI):
    """Verify all routes are properly registered"""
    print("Registered routes:")
    for route in app.routes:
        if hasattr(
            route, "path"
        ):  # Check if route has path attribute (exclude exceptions handlers etc.)
            print(f"{route.path} ({', '.join(route.methods)})")


if __name__ == "__main__":
    # from app.services.image_processor import ImageProcessor
    # import asyncio
    # processor = ImageProcessor()
    # test_response = asyncio.run(processor.process_image(
    #     "D:/Kushagra/Programming/DocsVerse/backend/data/processed/d57f3ef2-3138-4b4d-98a6-a4c70f2ce212.png"
    # ))
    # print("BACKEND RESPONSE:", test_response) 

    os.makedirs("data", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    verify_routes(app)  

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
