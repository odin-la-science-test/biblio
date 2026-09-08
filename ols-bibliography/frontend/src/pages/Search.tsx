import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { searchService, sourceService } from '../services/api';
import type { Document, Source } from '../types';
import { Search as SearchIcon, Loader2 } from 'lucide-react';

export default function Search() {
  const [query, setQuery] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const { data: sources } = useQuery({
    queryKey: ['sources'],
    queryFn: async () => {
      try {
        const response = await sourceService.getAll();
        return response.data;
      } catch (e) {
        return [];
      }
    }
  });

  const searchMutation = useMutation({
    mutationFn: () => searchService.federated(query, selectedSources.length > 0 ? selectedSources : undefined),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate();
    }
  };

  const toggleSource = (sourceId: string) => {
    setSelectedSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Recherche fédérée</h1>

      <form onSubmit={handleSearch} className="flex gap-4">
        <div className="flex-1 relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Rechercher des articles scientifiques..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        <button
          type="submit"
          disabled={searchMutation.isPending}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 flex items-center gap-2"
        >
          {searchMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
          Rechercher
        </button>
      </form>

      {sources && sources.length > 0 && (
        <div className="flex gap-4 flex-wrap">
          <span className="text-sm font-medium text-gray-700">Sources:</span>
          {sources.map(source => (
            <label key={source.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedSources.includes(source.id)}
                onChange={() => toggleSource(source.id)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">{source.name}</span>
            </label>
          ))}
        </div>
      )}

      {searchMutation.isPending && (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      )}

      {searchMutation.data && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            {searchMutation.data.data.total} résultats trouvés
          </p>
          <div className="grid gap-4">
            {searchMutation.data.data.documents.map((doc: Document) => (
              <DocumentCard key={doc.id} document={doc} />
            ))}
          </div>
        </div>
      )}

      {searchMutation.error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-lg">
          Erreur lors de la recherche. Veuillez réessayer.
        </div>
      )}
    </div>
  );
}

function DocumentCard({ document }: { document: Document }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {document.title}
      </h3>
      {document.authors && document.authors.length > 0 && (
        <p className="text-sm text-gray-600 mb-2">
          {document.authors.slice(0, 3).map(a => a.name).join(', ')}
          {document.authors.length > 3 && ` et ${document.authors.length - 3} autres`}
        </p>
      )}
      {document.abstract && (
        <p className="text-gray-700 text-sm mb-3 line-clamp-3">
          {document.abstract}
        </p>
      )}
      <div className="flex gap-4 text-xs text-gray-500">
        {document.publicationDate && (
          <span>{new Date(document.publicationDate).getFullYear()}</span>
        )}
        {document.doi && (
          <a href={`https://doi.org/${document.doi}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
            DOI: {document.doi}
          </a>
        )}
        {document.pmid && (
          <span>PMID: {document.pmid}</span>
        )}
      </div>
    </div>
  );
}
