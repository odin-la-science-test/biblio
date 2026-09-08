import axios from 'axios';
import type { 
  Document, Library, Folder, Tag, SavedSearch, 
  Watch, Source, SearchResults, Statistics 
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentService = {
  getAll: (params?: any) => api.get<Document[]>('/documents', { params }),
  getById: (id: string) => api.get<Document>(`/documents/${id}`),
  create: (data: Partial<Document>) => api.post<Document>('/documents', data),
  update: (id: string, data: Partial<Document>) => api.put<Document>(`/documents/${id}`, data),
  delete: (id: string) => api.delete(`/documents/${id}`),
};

export const libraryService = {
  getAll: () => api.get<Library[]>('/libraries'),
  getById: (id: string) => api.get<Library>(`/libraries/${id}`),
  create: (data: Partial<Library>) => api.post<Library>('/libraries', data),
  update: (id: string, data: Partial<Library>) => api.put<Library>(`/libraries/${id}`, data),
  delete: (id: string) => api.delete(`/libraries/${id}`),
};

export const folderService = {
  getAll: (libraryId: string) => api.get<Folder[]>(`/libraries/${libraryId}/folders`),
  getById: (id: string) => api.get<Folder>(`/folders/${id}`),
  create: (data: Partial<Folder>) => api.post<Folder>('/folders', data),
  update: (id: string, data: Partial<Folder>) => api.put<Folder>(`/folders/${id}`, data),
  delete: (id: string) => api.delete(`/folders/${id}`),
};

export const tagService = {
  getAll: (libraryId?: string) => api.get<Tag[]>('/tags', { params: { libraryId } }),
  create: (data: Partial<Tag>) => api.post<Tag>('/tags', data),
  update: (id: string, data: Partial<Tag>) => api.put<Tag>(`/tags/${id}`, data),
  delete: (id: string) => api.delete(`/tags/${id}`),
};

export const searchService = {
  federated: (query: string, sources?: string[]) => 
    api.post<SearchResults>('/search/federated', { query, sources }),
  saved: (id: string) => api.get<Document[]>(`/search/saved/${id}`),
};

export const watchService = {
  getAll: () => api.get<Watch[]>('/watches'),
  create: (data: Partial<Watch>) => api.post<Watch>('/watches', data),
  update: (id: string, data: Partial<Watch>) => api.put<Watch>(`/watches/${id}`, data),
  delete: (id: string) => api.delete(`/watches/${id}`),
  run: (id: string) => api.post(`/watches/${id}/run`),
};

export const sourceService = {
  getAll: () => api.get<Source[]>('/sources'),
  getCapabilities: (id: string) => api.get(`/sources/${id}/capabilities`),
};

export const statisticsService = {
  getOverview: () => api.get<Statistics>('/statistics/overview'),
  getByLibrary: (libraryId: string) => api.get<Statistics>(`/statistics/library/${libraryId}`),
};
