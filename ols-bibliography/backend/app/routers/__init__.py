"""
API routers for the OLS Bibliography module.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.models import (
    CanonicalDocument, Library, Folder, Tag, Source,
    Author, Keyword, SavedSearch, Watch, LibraryDocument
)
from app.schemas import (
    DocumentResponse, DocumentCreate, SearchQuery, SearchResponse,
    LibraryResponse, LibraryCreate, FolderResponse, FolderCreate,
    TagResponse, TagCreate, SavedSearchResponse, SavedSearchCreate,
    WatchResponse, WatchCreate, StatisticsResponse, StatisticsFacet,
    MessageResponse
)
from app.services.search_service import federated_search_service


# Create routers
documents_router = APIRouter(prefix="/api/documents", tags=["Documents"])
libraries_router = APIRouter(prefix="/api/libraries", tags=["Libraries"])
search_router = APIRouter(prefix="/api/search", tags=["Search"])
folders_router = APIRouter(prefix="/api/folders", tags=["Folders"])
tags_router = APIRouter(prefix="/api/tags", tags=["Tags"])
watches_router = APIRouter(prefix="/api/watches", tags=["Watches"])
statistics_router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


# ============== Documents Routes ==============

@documents_router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all canonical documents."""
    result = await db.execute(
        select(CanonicalDocument).offset(skip).limit(limit)
    )
    documents = result.scalars().all()
    return documents


@documents_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific document by ID."""
    result = await db.execute(
        select(CanonicalDocument).where(CanonicalDocument.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@documents_router.post("/", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new canonical document."""
    # Create authors if provided
    authors = []
    if document_data.author_ids:
        result = await db.execute(
            select(Author).where(Author.id.in_(document_data.author_ids))
        )
        authors = result.scalars().all()
    
    # Create keywords if provided
    keywords = []
    if document_data.keyword_ids:
        result = await db.execute(
            select(Keyword).where(Keyword.id.in_(document_data.keyword_ids))
        )
        keywords = result.scalars().all()
    
    # Create sources if provided
    sources = []
    if document_data.source_ids:
        result = await db.execute(
            select(Source).where(Source.id.in_(document_data.source_ids))
        )
        sources = result.scalars().all()
    
    # Create document
    document = CanonicalDocument(
        title=document_data.title,
        abstract=document_data.abstract,
        document_type=document_data.document_type,
        journal=document_data.journal,
        doi=document_data.doi,
        pmid=document_data.pmid,
        is_open_access=document_data.is_open_access,
        citation_count=document_data.citation_count or 0,
        authors=authors,
        keywords=keywords,
        sources=sources,
    )
    
    db.add(document)
    await db.flush()
    await db.refresh(document)
    
    return document


@documents_router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document."""
    result = await db.execute(
        select(CanonicalDocument).where(CanonicalDocument.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.delete(document)
    return MessageResponse(message="Document deleted successfully")


# ============== Libraries Routes ==============

@libraries_router.get("/", response_model=List[LibraryResponse])
async def list_libraries(db: AsyncSession = Depends(get_db)):
    """List all libraries."""
    result = await db.execute(select(Library))
    return result.scalars().all()


@libraries_router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(library_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific library."""
    result = await db.execute(
        select(Library).where(Library.id == library_id)
    )
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    return library


@libraries_router.post("/", response_model=LibraryResponse)
async def create_library(
    library_data: LibraryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new library."""
    library = Library(
        name=library_data.name,
        library_type=library_data.library_type,
        user_id=library_data.user_id,
        laboratory_id=library_data.laboratory_id,
    )
    
    db.add(library)
    await db.flush()
    await db.refresh(library)
    
    return library


# ============== Search Routes ==============

@search_router.post("/", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute federated search across multiple sources.
    
    Implements section 21: Federated Search Architecture.
    Returns normalized and deduplicated results with statistics.
    """
    import time
    start_time = time.time()
    
    # Execute federated search
    source_ids = query.source_ids if query.source_ids else None
    results = await federated_search_service.search(query, source_ids)
    
    # Get statistics
    stats = federated_search_service.get_statistics(results)
    
    search_time_ms = (time.time() - start_time) * 1000
    
    # Convert results to DocumentResponse format
    # For now, we'll create simplified responses
    document_responses = []
    for result in results[:50]:  # Limit for response
        doc = {
            "title": result.get("title", ""),
            "abstract": result.get("abstract"),
            "journal": result.get("journal"),
            "doi": result.get("doi"),
            "pmid": result.get("pmid"),
            "is_open_access": result.get("is_open_access", False),
            "citation_count": result.get("citation_count", 0),
        }
        document_responses.append(doc)
    
    return SearchResponse(
        query=query.query_text or "",
        total_results=len(results),
        results=document_responses,
        facets={
            "by_year": stats["by_year"],
            "by_document_type": stats["by_document_type"],
            "by_journal": stats["by_journal"],
            "by_source": stats["by_source"],
            "open_access_count": stats["open_access_count"],
        },
        search_time_ms=search_time_ms
    )


@search_router.get("/sources", response_model=List[str])
async def list_sources():
    """List available search sources."""
    return [
        "PubMed",
        "Europe PMC",
        "OpenAlex",
        "Crossref",
        "Semantic Scholar",
        "DOAJ",
        "CORE",
    ]


# ============== Folders Routes ==============

@folders_router.get("/", response_model=List[FolderResponse])
async def list_folders(
    library_id: Optional[int] = Query(None),
    parent_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List folders, optionally filtered by library and parent."""
    stmt = select(Folder)
    
    if library_id:
        stmt = stmt.where(Folder.library_id == library_id)
    
    if parent_id is not None:
        if parent_id == -1:
            # Root folders only
            stmt = stmt.where(Folder.parent_id.is_(None))
        else:
            stmt = stmt.where(Folder.parent_id == parent_id)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@folders_router.post("/", response_model=FolderResponse)
async def create_folder(
    folder_data: FolderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder."""
    folder = Folder(
        name=folder_data.name,
        description=folder_data.description,
        parent_id=folder_data.parent_id,
        library_id=folder_data.library_id,
    )
    
    db.add(folder)
    await db.flush()
    await db.refresh(folder)
    
    return folder


# ============== Tags Routes ==============

@tags_router.get("/", response_model=List[TagResponse])
async def list_tags(
    library_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List tags, optionally filtered by library."""
    stmt = select(Tag)
    
    if library_id:
        stmt = stmt.where(Tag.library_id == library_id)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@tags_router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag."""
    tag = Tag(
        name=tag_data.name,
        color=tag_data.color,
        library_id=tag_data.library_id,
    )
    
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    
    return tag


# ============== Saved Searches Routes ==============

@search_router.get("/saved", response_model=List[SavedSearchResponse])
async def list_saved_searches(
    library_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List saved searches."""
    stmt = select(SavedSearch)
    
    if library_id:
        stmt = stmt.where(SavedSearch.library_id == library_id)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@search_router.post("/saved", response_model=SavedSearchResponse)
async def save_search(
    search_data: SavedSearchCreate,
    db: AsyncSession = Depends(get_db)
):
    """Save a search for later execution."""
    saved_search = SavedSearch(
        name=search_data.name,
        description=search_data.description,
        query_text=search_data.query_text,
        filters=str(search_data.filters) if search_data.filters else None,
        sources=str(search_data.sources) if search_data.sources else None,
        library_id=search_data.library_id,
        created_by=1,  # TODO: Get from authentication
        is_dynamic=search_data.is_dynamic,
    )
    
    db.add(saved_search)
    await db.flush()
    await db.refresh(saved_search)
    
    return saved_search


# ============== Watches Routes ==============

@watches_router.get("/", response_model=List[WatchResponse])
async def list_watches(
    db: AsyncSession = Depends(get_db)
):
    """List all watches."""
    result = await db.execute(select(Watch))
    return result.scalars().all()


@watches_router.post("/", response_model=WatchResponse)
async def create_watch(
    watch_data: WatchCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new watch/alert."""
    watch = Watch(
        name=watch_data.name,
        watch_type=watch_data.watch_type,
        target_id=watch_data.target_id,
        target_type=watch_data.target_type,
        search_criteria=str(watch_data.search_criteria) if watch_data.search_criteria else None,
        check_frequency=watch_data.check_frequency,
        notify_on_new=watch_data.notify_on_new,
        notify_on_citations=watch_data.notify_on_citations,
        notify_on_corrections=watch_data.notify_on_corrections,
        notify_on_retractions=watch_data.notify_on_retractions,
        created_by=1,  # TODO: Get from authentication
        library_id=watch_data.library_id,
    )
    
    db.add(watch)
    await db.flush()
    await db.refresh(watch)
    
    return watch


# ============== Statistics Routes ==============

@statistics_router.get("/context", response_model=StatisticsResponse)
async def get_context_statistics(
    context_type: str = Query(..., pattern="^(search|library)$"),
    context_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get contextual statistics (section 5.3).
    
    Statistics are always relative to the current context:
    - Search results
    - Library collection
    """
    total_documents = 0
    by_year = []
    by_document_type = []
    
    if context_type == "library" and context_id:
        # Get statistics for library
        result = await db.execute(
            select(func.count(LibraryDocument.document_id)).where(
                LibraryDocument.library_id == context_id
            )
        )
        total_documents = result.scalar() or 0
        
        # Get year distribution
        year_result = await db.execute(
            select(
                func.strftime('%Y', CanonicalDocument.publication_date).label('year'),
                func.count().label('count')
            )
            .join(CanonicalDocument, CanonicalDocument.id == LibraryDocument.document_id)
            .where(LibraryDocument.library_id == context_id)
            .group_by(func.strftime('%Y', CanonicalDocument.publication_date))
        )
        
        by_year = [
            StatisticsFacet(name=str(row[0]), count=row[1], percentage=0)
            for row in year_result.all()
        ]
        
        # Calculate percentages
        if total_documents > 0:
            for facet in by_year:
                facet.percentage = (facet.count / total_documents) * 100
    
    elif context_type == "search":
        # For search, statistics would be computed from search results
        # This is handled in the search endpoint
        total_documents = 0
    
    return StatisticsResponse(
        context_type=context_type,
        context_id=context_id,
        total_documents=total_documents,
        by_year=by_year if by_year else None,
        by_document_type=by_document_type if by_document_type else None,
    )
