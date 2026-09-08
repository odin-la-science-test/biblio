"""
Pydantic schemas for request/response validation.

These schemas implement the API contracts based on the technical specification.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ============== User Schemas ==============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Laboratory Schemas ==============

class LaboratoryBase(BaseModel):
    """Base laboratory schema."""
    name: str
    description: Optional[str] = None


class LaboratoryCreate(LaboratoryBase):
    """Schema for creating a laboratory."""
    pass


class LaboratoryResponse(LaboratoryBase):
    """Schema for laboratory response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Library Schemas ==============

class LibraryBase(BaseModel):
    """Base library schema."""
    name: str
    library_type: str = Field(..., description="Type: 'personal' or 'laboratory'")


class LibraryCreate(LibraryBase):
    """Schema for creating a library."""
    user_id: Optional[int] = None
    laboratory_id: Optional[int] = None


class LibraryResponse(LibraryBase):
    """Schema for library response."""
    id: int
    user_id: Optional[int]
    laboratory_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Folder Schemas ==============

class FolderBase(BaseModel):
    """Base folder schema."""
    name: str
    description: Optional[str] = None


class FolderCreate(FolderBase):
    """Schema for creating a folder."""
    parent_id: Optional[int] = None
    library_id: int


class FolderResponse(FolderBase):
    """Schema for folder response."""
    id: int
    parent_id: Optional[int]
    library_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Tag Schemas ==============

class TagBase(BaseModel):
    """Base tag schema."""
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    """Schema for creating a tag."""
    library_id: int


class TagResponse(TagBase):
    """Schema for tag response."""
    id: int
    library_id: int
    
    class Config:
        from_attributes = True


# ============== Author Schemas ==============

class AuthorBase(BaseModel):
    """Base author schema."""
    name: str
    orcid: Optional[str] = None
    affiliation: Optional[str] = None


class AuthorResponse(AuthorBase):
    """Schema for author response."""
    id: int
    
    class Config:
        from_attributes = True


# ============== Keyword Schemas ==============

class KeywordBase(BaseModel):
    """Base keyword schema."""
    name: str
    keyword_type: Optional[str] = None


class KeywordResponse(KeywordBase):
    """Schema for keyword response."""
    id: int
    
    class Config:
        from_attributes = True


# ============== Source Schemas ==============

class SourceBase(BaseModel):
    """Base source schema."""
    name: str
    api_url: Optional[str] = None
    is_active: bool = True


class SourceCapabilities(BaseModel):
    """Source capabilities (section 23)."""
    supports_boolean: bool = False
    supports_phrase_search: bool = False
    supports_title_search: bool = False
    supports_abstract_search: bool = False
    supports_author_search: bool = False
    supports_date_filter: bool = False
    supports_journal_filter: bool = False
    supports_institution_filter: bool = False
    supports_open_access_filter: bool = False
    supports_citations: bool = False
    supports_semantic_search: bool = False


class SourceResponse(SourceBase, SourceCapabilities):
    """Schema for source response."""
    id: int
    
    class Config:
        from_attributes = True


# ============== Document Schemas ==============

class DocumentIdentifier(BaseModel):
    """Document identifiers (section 15)."""
    doi: Optional[str] = None
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    openalex_id: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None


class DocumentBase(DocumentIdentifier):
    """Base document schema."""
    title: str
    abstract: Optional[str] = None
    document_type: Optional[str] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    is_open_access: bool = False
    license: Optional[str] = None
    full_text_url: Optional[str] = None
    pdf_url: Optional[str] = None
    citation_count: Optional[int] = 0
    influence_score: Optional[float] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    author_ids: Optional[List[int]] = []
    keyword_ids: Optional[List[int]] = []
    source_ids: Optional[List[int]] = []


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    creator_id: Optional[int] = None
    authors: Optional[List[AuthorResponse]] = []
    keywords: Optional[List[KeywordResponse]] = []
    sources: Optional[List[SourceResponse]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LibraryDocumentBase(BaseModel):
    """Base library document schema (section 13)."""
    status: Optional[str] = None  # 'to_read', 'reading', 'read', 'important', 'archived'
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class LibraryDocumentCreate(LibraryDocumentBase):
    """Schema for adding document to library."""
    document_id: int
    library_id: int


class LibraryDocumentResponse(LibraryDocumentBase):
    """Schema for library document response."""
    id: int
    document_id: int
    library_id: int
    added_by: Optional[int] = None
    added_at: datetime
    document: Optional[DocumentResponse] = None
    
    class Config:
        from_attributes = True


# ============== Search Schemas ==============

class SearchQuery(BaseModel):
    """
    Abstract search query model (section 22).
    
    Independent of specific source syntax.
    """
    query_text: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[List[str]] = []
    journal: Optional[str] = None
    institution: Optional[str] = None
    publication_date_from: Optional[datetime] = None
    publication_date_to: Optional[datetime] = None
    document_type: Optional[str] = None
    is_open_access: Optional[bool] = None
    keywords: Optional[List[str]] = []
    exclude_terms: Optional[List[str]] = []
    source_ids: Optional[List[int]] = []
    boolean_operator: Optional[str] = Field("AND", pattern="^(AND|OR|NOT)$")
    use_semantic_search: bool = False


class SavedSearchBase(BaseModel):
    """Base saved search schema (section 12)."""
    name: str
    description: Optional[str] = None


class SavedSearchCreate(SavedSearchBase):
    """Schema for creating a saved search."""
    query_text: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None
    library_id: int
    is_dynamic: bool = True


class SavedSearchResponse(SavedSearchBase):
    """Schema for saved search response."""
    id: int
    query_text: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None
    library_id: int
    created_by: int
    is_dynamic: bool
    created_at: datetime
    last_executed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Search result item."""
    document: DocumentResponse
    relevance_score: Optional[float] = None
    sources: List[str] = []


class SearchResponse(BaseModel):
    """Search response with results and statistics."""
    query: str
    total_results: int
    results: List[DocumentResponse]
    facets: Optional[Dict[str, Any]] = None  # Statistics/facets
    search_time_ms: float


# ============== Watch/Alert Schemas ==============

class WatchBase(BaseModel):
    """Base watch schema (section 5.4)."""
    name: str
    watch_type: str  # 'search', 'document', 'author', 'journal', 'institution', 'topic'


class WatchCreate(WatchBase):
    """Schema for creating a watch."""
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    search_criteria: Optional[Dict[str, Any]] = None
    check_frequency: str = "daily"
    notify_on_new: bool = True
    notify_on_citations: bool = False
    notify_on_corrections: bool = False
    notify_on_retractions: bool = False
    library_id: Optional[int] = None


class WatchResponse(WatchBase):
    """Schema for watch response."""
    id: int
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    check_frequency: str
    is_active: bool
    notify_on_new: bool
    notify_on_citations: bool
    notify_on_corrections: bool
    notify_on_retractions: bool
    created_by: int
    library_id: Optional[int] = None
    created_at: datetime
    last_check_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WatchEventBase(BaseModel):
    """Base watch event schema."""
    event_type: str  # 'new_publication', 'citation', 'correction', 'retraction', 'new_version'


class WatchEventResponse(WatchEventBase):
    """Schema for watch event response."""
    id: int
    watch_id: int
    document_id: Optional[int] = None
    event_data: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    is_notified: bool
    detected_at: datetime
    
    class Config:
        from_attributes = True


# ============== Statistics Schemas ==============

class StatisticsFacet(BaseModel):
    """Statistics facet for contextual statistics."""
    name: str
    count: int
    percentage: float


class StatisticsResponse(BaseModel):
    """
    Contextual statistics response (section 5.3).
    
    Statistics are always relative to the current context
    (search results or library collection).
    """
    context_type: str  # 'search' or 'library'
    context_id: Optional[int] = None
    total_documents: int
    
    # Facets
    by_year: Optional[List[StatisticsFacet]] = None
    by_document_type: Optional[List[StatisticsFacet]] = None
    by_journal: Optional[List[StatisticsFacet]] = None
    by_author: Optional[List[StatisticsFacet]] = None
    by_source: Optional[List[StatisticsFacet]] = None
    by_open_access: Optional[List[StatisticsFacet]] = None
    
    # Metrics
    average_citations: Optional[float] = None
    open_access_percentage: Optional[float] = None


# ============== Authentication Schemas ==============

class Token(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    user_id: Optional[int] = None


# ============== Generic Response Schemas ==============

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
