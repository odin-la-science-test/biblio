"""
Database models for the OLS Bibliography module.

This module implements the data model as specified in the technical specification:
- Canonical document identity (section 14)
- Separation between document and library membership (section 8)
- Multiple memberships (section 9)
- Hierarchical organization (section 10)
- Personal and laboratory libraries (sections 6-7)
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table, Float
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


# Association tables for many-to-many relationships
document_sources = Table(
    'document_sources',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('canonical_documents.id'), primary_key=True),
    Column('source_id', Integer, ForeignKey('sources.id'), primary_key=True)
)

document_authors = Table(
    'document_authors',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('canonical_documents.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

document_keywords = Table(
    'document_keywords',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('canonical_documents.id'), primary_key=True),
    Column('keyword_id', Integer, ForeignKey('keywords.id'), primary_key=True)
)

# Document-Folder many-to-many (section 9: multiple memberships)
document_folders = Table(
    'document_folders',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('canonical_documents.id'), primary_key=True),
    Column('folder_id', Integer, ForeignKey('folders.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)

# Document-Tag many-to-many (section 11)
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('canonical_documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class User(Base):
    """User model for personal libraries and authentication."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    personal_library: Mapped["Library"] = relationship("Library", back_populates="user", uselist=False)
    lab_memberships: Mapped[List["LabMembership"]] = relationship("LabMembership", back_populates="user")
    created_documents: Mapped[List["CanonicalDocument"]] = relationship("CanonicalDocument", back_populates="creator")


class Laboratory(Base):
    """Laboratory model for shared libraries (section 7)."""
    __tablename__ = 'laboratories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    library: Mapped["Library"] = relationship("Library", back_populates="laboratory", uselist=False)
    members: Mapped[List["LabMembership"]] = relationship("LabMembership", back_populates="laboratory")


class LabMembership(Base):
    """Association between users and laboratories."""
    __tablename__ = 'lab_memberships'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    lab_id: Mapped[int] = mapped_column(Integer, ForeignKey('laboratories.id'), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default='member')  # admin, member, viewer
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lab_memberships")
    laboratory: Mapped["Laboratory"] = relationship("Laboratory", back_populates="members")


class Library(Base):
    """
    Library model (sections 5.1, 6, 7).
    
    A library can be personal (linked to a user) or laboratory (linked to a lab).
    This implements the separation between document and library membership (section 8).
    """
    __tablename__ = 'libraries'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    library_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'personal' or 'laboratory'
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    laboratory_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('laboratories.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="personal_library")
    laboratory: Mapped[Optional["Laboratory"]] = relationship("Laboratory", back_populates="library")
    folders: Mapped[List["Folder"]] = relationship("Folder", back_populates="library", cascade="all, delete-orphan")
    documents: Mapped[List["LibraryDocument"]] = relationship("LibraryDocument", back_populates="library", cascade="all, delete-orphan")
    saved_searches: Mapped[List["SavedSearch"]] = relationship("SavedSearch", back_populates="library", cascade="all, delete-orphan")


class Folder(Base):
    """
    Folder model for hierarchical organization (section 10).
    
    Supports unlimited nesting levels for organizing documents.
    A document can belong to multiple folders (section 9).
    """
    __tablename__ = 'folders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('folders.id'), nullable=True)
    library_id: Mapped[int] = mapped_column(Integer, ForeignKey('libraries.id'), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    parent: Mapped[Optional["Folder"]] = relationship("Folder", remote_side=[id], backref="subfolders")
    library: Mapped["Library"] = relationship("Library", back_populates="folders")
    documents: Mapped[List["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        secondary=document_folders,
        backref="folders"
    )


class Tag(Base):
    """
    Tag model for transversal characterization (section 11).
    
    Tags are distinct from folders:
    - Folder = organization
    - Tag = characterization
    """
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    library_id: Mapped[int] = mapped_column(Integer, ForeignKey('libraries.id'), nullable=False)
    
    # Relationships
    library: Mapped["Library"] = relationship("Library", back_populates="tags")
    documents: Mapped[List["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        secondary=document_tags,
        backref="tags"
    )
    
    def __repr__(self):
        return f"<Tag(name='{self.name}', library_id={self.library_id})>"


class Source(Base):
    """
    External source model (section 20).
    
    Represents bibliographic data sources like PubMed, Europe PMC, OpenAlex, etc.
    Each source declares its capabilities (section 23).
    """
    __tablename__ = 'sources'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    api_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Capabilities (section 23)
    supports_boolean: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_phrase_search: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_title_search: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_abstract_search: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_author_search: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_date_filter: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_journal_filter: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_institution_filter: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_open_access_filter: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_citations: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_semantic_search: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    documents: Mapped[List["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        secondary=document_sources,
        backref="sources"
    )


class Author(Base):
    """Author model for document authors."""
    __tablename__ = 'authors'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    orcid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    affiliation: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    documents: Mapped[List["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        secondary=document_authors,
        backref="authors"
    )


class Keyword(Base):
    """Keyword/mesh term model."""
    __tablename__ = 'keywords'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    keyword_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'mesh', 'author', 'auto'
    
    # Relationships
    documents: Mapped[List["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        secondary=document_keywords,
        backref="keywords"
    )


class CanonicalDocument(Base):
    """
    Canonical document model (section 14).
    
    Represents a unique scientific work independent of the sources that provided it.
    Implements deduplication (section 16) by grouping multiple occurrences of the same work.
    """
    __tablename__ = 'canonical_documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Core metadata (section 17)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # article, review, preprint, etc.
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    volume: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issue: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pages: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Identifiers (section 15)
    doi: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    pmid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    openalex_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    semantic_scholar_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Access information
    is_open_access: Mapped[bool] = mapped_column(Boolean, default=False)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_text_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Metrics
    citation_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    influence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    creator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="created_documents")
    
    # Many-to-many relationships
    authors: Mapped[List["Author"]] = relationship(
        "Author",
        secondary=document_authors,
        back_populates="documents"
    )
    keywords: Mapped[List["Keyword"]] = relationship(
        "Keyword",
        secondary=document_keywords,
        back_populates="documents"
    )
    sources: Mapped[List["Source"]] = relationship(
        "Source",
        secondary=document_sources,
        back_populates="documents"
    )
    folders: Mapped[List["Folder"]] = relationship(
        "Folder",
        secondary=document_folders,
        back_populates="documents"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=document_tags,
        back_populates="documents"
    )
    
    # Document relationships (section 34)
    parent_document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('canonical_documents.id'), nullable=True)
    parent_document: Mapped[Optional["CanonicalDocument"]] = relationship(
        "CanonicalDocument",
        remote_side=[id],
        backref="child_documents"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CanonicalDocument(title='{self.title[:50]}...', doi='{self.doi}')>"


class LibraryDocument(Base):
    """
    Association between canonical documents and libraries.
    
    Implements section 8: separation between document and library membership.
    Stores context-specific metadata like status, notes, etc. (section 13).
    """
    __tablename__ = 'library_documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('canonical_documents.id'), nullable=False)
    library_id: Mapped[int] = mapped_column(Integer, ForeignKey('libraries.id'), nullable=False)
    
    # Context-specific metadata (section 13)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'to_read', 'reading', 'read', 'important', 'archived'
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    
    # Provenance (section 18)
    added_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    document: Mapped["CanonicalDocument"] = relationship("CanonicalDocument", backref="library_memberships")
    library: Mapped["Library"] = relationship("Library", back_populates="documents")
    
    __table_args__ = (
        # Ensure unique document-library pairs
        {'sqlite_autoincrement': True}
    )


class SavedSearch(Base):
    """
    Saved search / dynamic collection model (section 12).
    
    Represents a search that can be re-executed to get updated results.
    Can serve as entry point for alerts/watch (section 12).
    """
    __tablename__ = 'saved_searches'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Search criteria (section 22)
    query_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded filters
    sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded source list
    
    library_id: Mapped[int] = mapped_column(Integer, ForeignKey('libraries.id'), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    library: Mapped["Library"] = relationship("Library", back_populates="saved_searches")
    
    def __repr__(self):
        return f"<SavedSearch(name='{self.name}')>"


class Watch(Base):
    """
    Watch/Alert model (section 5.4, sections 72-83).
    
    Monitors various entities over time:
    - New publications matching a search
    - Citations of a document
    - Similar articles
    - Preprint → publication transitions
    - Corrections and retractions
    """
    __tablename__ = 'watches'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    watch_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'search', 'document', 'author', 'journal', 'institution', 'topic'
    
    # Target of the watch
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Could reference document, author, etc.
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    search_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # For search-based watches
    
    # Watch configuration
    check_frequency: Mapped[str] = mapped_column(String(20), default='daily')  # 'hourly', 'daily', 'weekly'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_new: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_citations: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_on_corrections: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_on_retractions: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    library_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('libraries.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Watch(name='{self.name}', type='{self.watch_type}')>"


class WatchEvent(Base):
    """
    Events detected by watches.
    
    Stores historical results of watch executions (section 115).
    """
    __tablename__ = 'watch_events'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    watch_id: Mapped[int] = mapped_column(Integer, ForeignKey('watches.id'), nullable=False)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('canonical_documents.id'), nullable=True)
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'new_publication', 'citation', 'correction', 'retraction', 'new_version'
    event_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded event details
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    watch: Mapped["Watch"] = relationship("Watch", backref="events")
    document: Mapped[Optional["CanonicalDocument"]] = relationship("CanonicalDocument")
    
    def __repr__(self):
        return f"<WatchEvent(type='{self.event_type}', detected_at='{self.detected_at}')>"


class DocumentSourceOccurrence(Base):
    """
    Tracks individual occurrences of a canonical document in different sources.
    
    Implements section 14: a canonical document can have multiple occurrences
    from PubMed, Europe PMC, OpenAlex, Crossref, etc.
    """
    __tablename__ = 'document_source_occurrences'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    canonical_document_id: Mapped[int] = mapped_column(Integer, ForeignKey('canonical_documents.id'), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey('sources.id'), nullable=False)
    source_document_id: Mapped[str] = mapped_column(String(255), nullable=False)  # ID in the external source
    
    # Raw metadata from source
    raw_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded
    
    # Provenance (section 18)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    canonical_document: Mapped["CanonicalDocument"] = relationship("CanonicalDocument")
    source: Mapped["Source"] = relationship("Source")
    
    __table_args__ = (
        # Unique constraint for source + source_document_id
        {'sqlite_autoincrement': True}
    )
