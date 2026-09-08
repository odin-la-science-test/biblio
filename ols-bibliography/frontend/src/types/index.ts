export interface Author {
  name: string;
  affiliation?: string;
}

export interface Document {
  id: string;
  title: string;
  abstract?: string;
  authors: Author[];
  publicationDate?: string;
  doi?: string;
  pmid?: string;
  sourceId: string;
  canonicalId?: string;
  metadata: Record<string, any>;
}

export interface Library {
  id: string;
  name: string;
  description?: string;
  isPersonal: boolean;
  ownerId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Folder {
  id: string;
  name: string;
  parentId?: string;
  libraryId: string;
  path: string;
  children?: Folder[];
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  libraryId?: string;
}

export interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters?: Record<string, any>;
  libraryId?: string;
}

export interface Watch {
  id: string;
  name: string;
  query: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  lastRun?: string;
  isActive: boolean;
}

export interface Source {
  id: string;
  name: string;
  type: 'pubmed' | 'openalex' | 'crossref' | 'custom';
  capabilities: {
    search: boolean;
    fullText: boolean;
    citations: boolean;
    references: boolean;
  };
  isActive: boolean;
}

export interface SearchResults {
  documents: Document[];
  total: number;
  source: string;
  facets?: Record<string, any>;
}

export interface Statistics {
  totalDocuments: number;
  documentsByYear: Record<number, number>;
  documentsBySource: Record<string, number>;
  topAuthors: { name: string; count: number }[];
}
