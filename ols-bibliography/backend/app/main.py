"""
Main FastAPI application for OLS Bibliography module.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import (
    documents_router, libraries_router, search_router,
    folders_router, tags_router, watches_router, statistics_router
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## OLS Bibliography Module API

A scientific bibliography management system implementing:

- **Federated Search**: Search across multiple sources (PubMed, OpenAlex, Crossref, etc.)
- **Canonical Documents**: Unique document identity with deduplication
- **Personal & Laboratory Libraries**: Separate personal and shared library spaces
- **Hierarchical Organization**: Folders and subfolders for organization
- **Tags**: Transversal characterization of documents
- **Saved Searches**: Dynamic collections based on search criteria
- **Watches/Alerts**: Monitor new publications, citations, corrections
- **Contextual Statistics**: Real-time statistics about current context

### Key Features

#### Search (Section 21-32)
- Federated search architecture
- Query adaptation to source capabilities
- Result normalization and deduplication
- Progressive results loading

#### Library Management (Sections 5.1, 6-13)
- Personal and laboratory libraries
- Hierarchical folder structure
- Tag-based characterization
- Document status tracking

#### Watches (Sections 72-83)
- New publication alerts
- Citation monitoring
- Correction/retraction detection
- Preprint to publication tracking
    """,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents_router)
app.include_router(libraries_router)
app.include_router(search_router)
app.include_router(folders_router)
app.include_router(tags_router)
app.include_router(watches_router)
app.include_router(statistics_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Scientific Bibliography Management System",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
