"""
Tests for the OLS Bibliography backend.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base, CanonicalDocument, Library, Folder, Tag


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=type(get_db.__annotations__['return']).__args__[0],
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_engine):
    """Create test HTTP client."""
    async def override_get_db():
        async_session = async_sessionmaker(
            test_engine,
            class_=type(get_db.__annotations__['return']).__args__[0],
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============== Health Check Tests ==============

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "OLS Bibliography"


# ============== Document Tests ==============

@pytest.mark.asyncio
async def test_create_document(client):
    """Test creating a document."""
    document_data = {
        "title": "Test Scientific Article",
        "abstract": "This is a test abstract",
        "document_type": "article",
        "journal": "Test Journal",
        "doi": "10.1234/test.2024",
        "is_open_access": True,
    }
    
    response = await client.post("/api/documents/", json=document_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == document_data["title"]
    assert data["doi"] == document_data["doi"]


@pytest.mark.asyncio
async def test_list_documents(client):
    """Test listing documents."""
    # Create a document first
    document_data = {
        "title": "Test Article",
        "abstract": "Test abstract",
    }
    await client.post("/api/documents/", json=document_data)
    
    response = await client.get("/api/documents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_document(client):
    """Test getting a specific document."""
    # Create a document first
    document_data = {
        "title": "Specific Test Article",
        "abstract": "Test abstract",
        "doi": "10.1234/specific.2024",
    }
    create_response = await client.post("/api/documents/", json=document_data)
    document_id = create_response.json()["id"]
    
    response = await client.get(f"/api/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == document_data["title"]


@pytest.mark.asyncio
async def test_get_nonexistent_document(client):
    """Test getting a nonexistent document."""
    response = await client.get("/api/documents/99999")
    assert response.status_code == 404


# ============== Library Tests ==============

@pytest.mark.asyncio
async def test_create_library(client):
    """Test creating a library."""
    library_data = {
        "name": "Test Personal Library",
        "library_type": "personal",
    }
    
    response = await client.post("/api/libraries/", json=library_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == library_data["name"]
    assert data["library_type"] == library_data["library_type"]


@pytest.mark.asyncio
async def test_list_libraries(client):
    """Test listing libraries."""
    response = await client.get("/api/libraries/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============== Search Tests ==============

@pytest.mark.asyncio
async def test_search_basic(client):
    """Test basic search."""
    search_data = {
        "query_text": "CRISPR gene editing",
    }
    
    response = await client.post("/api/search/", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "results" in data


@pytest.mark.asyncio
async def test_search_with_filters(client):
    """Test search with filters."""
    search_data = {
        "query_text": "cancer treatment",
        "document_type": "review",
        "is_open_access": True,
        "boolean_operator": "AND",
    }
    
    response = await client.post("/api/search/", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "facets" in data


@pytest.mark.asyncio
async def test_list_sources(client):
    """Test listing available sources."""
    response = await client.get("/api/search/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "PubMed" in data
    assert "OpenAlex" in data


# ============== Folder Tests ==============

@pytest.mark.asyncio
async def test_create_folder(client):
    """Test creating a folder."""
    # First create a library
    library_data = {"name": "Test Library", "library_type": "personal"}
    library_response = await client.post("/api/libraries/", json=library_data)
    library_id = library_response.json()["id"]
    
    folder_data = {
        "name": "CRISPR Papers",
        "library_id": library_id,
    }
    
    response = await client.post("/api/folders/", json=folder_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == folder_data["name"]
    assert data["library_id"] == library_id


@pytest.mark.asyncio
async def test_create_subfolder(client):
    """Test creating a subfolder."""
    # Create library and parent folder
    library_data = {"name": "Test Library", "library_type": "personal"}
    library_response = await client.post("/api/libraries/", json=library_data)
    library_id = library_response.json()["id"]
    
    parent_folder_data = {"name": "Parent Folder", "library_id": library_id}
    parent_response = await client.post("/api/folders/", json=parent_folder_data)
    parent_id = parent_response.json()["id"]
    
    # Create subfolder
    subfolder_data = {
        "name": "Subfolder",
        "library_id": library_id,
        "parent_id": parent_id,
    }
    
    response = await client.post("/api/folders/", json=subfolder_data)
    assert response.status_code == 200
    data = response.json()
    assert data["parent_id"] == parent_id


# ============== Tag Tests ==============

@pytest.mark.asyncio
async def test_create_tag(client):
    """Test creating a tag."""
    # First create a library
    library_data = {"name": "Test Library", "library_type": "personal"}
    library_response = await client.post("/api/libraries/", json=library_data)
    library_id = library_response.json()["id"]
    
    tag_data = {
        "name": "Important",
        "color": "#FF0000",
        "library_id": library_id,
    }
    
    response = await client.post("/api/tags/", json=tag_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["color"] == tag_data["color"]


# ============== Watch Tests ==============

@pytest.mark.asyncio
async def test_create_watch(client):
    """Test creating a watch."""
    watch_data = {
        "name": "CRISPR New Publications",
        "watch_type": "search",
        "check_frequency": "daily",
        "notify_on_new": True,
    }
    
    response = await client.post("/api/watches/", json=watch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == watch_data["name"]
    assert data["watch_type"] == watch_data["watch_type"]
    assert data["is_active"] == True


# ============== Statistics Tests ==============

@pytest.mark.asyncio
async def test_get_statistics(client):
    """Test getting contextual statistics."""
    response = await client.get("/api/statistics/context?context_type=library")
    assert response.status_code == 200
    data = response.json()
    assert "context_type" in data
    assert "total_documents" in data


# ============== Deduplication Tests ==============

@pytest.mark.asyncio
async def test_deduplication_by_doi():
    """Test that documents with same DOI are deduplicated."""
    from app.services.search_service import FederatedSearchService
    
    service = FederatedSearchService()
    
    # Create test results with same DOI
    results = [
        {
            "title": "Test Article",
            "doi": "10.1234/test.2024",
            "_source": "PubMed",
        },
        {
            "title": "Test Article",
            "doi": "10.1234/test.2024",
            "_source": "Crossref",
        },
        {
            "title": "Different Article",
            "doi": "10.1234/different.2024",
            "_source": "OpenAlex",
        },
    ]
    
    deduplicated = service.deduplicate_results(results)
    
    # Should have 2 unique documents
    assert len(deduplicated) == 2
    
    # The first document should have both sources
    doi_doc = next(d for d in deduplicated if d["doi"] == "10.1234/test.2024")
    assert len(doi_doc["_all_sources"]) == 2


# ============== Search Query Adaptation Tests ==============

@pytest.mark.asyncio
async def test_pubmed_query_adaptation():
    """Test PubMed query adaptation."""
    from app.services.search_service import PubMedConnector
    from app.schemas import SearchQuery
    from datetime import datetime
    
    connector = PubMedConnector()
    
    query = SearchQuery(
        query_text="CRISPR",
        title="gene editing",
        authors=["Doudna"],
        document_type="review",
        boolean_operator="AND",
    )
    
    pubmed_query = connector.adapt_query(query)
    
    assert "[All Fields]" in pubmed_query
    assert "[Title]" in pubmed_query
    assert "[Author]" in pubmed_query
    assert "[Publication Type]" in pubmed_query


@pytest.mark.asyncio
async def test_openalex_normalization():
    """Test OpenAlex result normalization."""
    from app.services.search_service import OpenAlexConnector
    
    connector = OpenAlexConnector()
    
    raw_result = {
        "title": "Test Article",
        "abstract": "Test abstract",
        "authorships": [
            {"author": {"display_name": "John Doe", "orcid": "https://orcid.org/0000-0000-0000-0000"}}
        ],
        "primary_location": {"source": {"display_name": "Nature"}},
        "publication_date": "2024-01-15",
        "doi": "https://doi.org/10.1234/test",
        "id": "https://openalex.org/W1234567890",
        "open_access": {"is_oa": True},
        "type": "journal-article",
        "cited_by_count": 42,
    }
    
    normalized = connector.normalize_result(raw_result)
    
    assert normalized["title"] == "Test Article"
    assert normalized["is_open_access"] == True
    assert normalized["citation_count"] == 42
    assert "W1234567890" in normalized["openalex_id"]


# Run with: pytest tests/ -v
