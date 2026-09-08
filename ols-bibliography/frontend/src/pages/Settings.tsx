import { useQuery } from '@tanstack/react-query';
import { sourceService } from '../services/api';
import type { Source } from '../types';
import { Database, Check, X } from 'lucide-react';

export default function Settings() {
  const { data: sources, isLoading } = useQuery({
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

  if (isLoading) {
    return <div className="flex justify-center py-12">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Paramètres</h1>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Sources de données</h2>
          <p className="text-sm text-gray-500 mt-1">
            Configurez les connecteurs vers les bases de données scientifiques
          </p>
        </div>

        <div className="divide-y">
          {sources && sources.map((source: Source) => (
            <div key={source.id} className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-indigo-100 p-2 rounded-lg">
                  <Database className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{source.name}</h3>
                  <p className="text-sm text-gray-500 capitalize">{source.type}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="flex gap-4 text-sm">
                  <Capability label="Recherche" enabled={source.capabilities.search} />
                  <Capability label="Texte complet" enabled={source.capabilities.fullText} />
                  <Capability label="Citations" enabled={source.capabilities.citations} />
                  <Capability label="Références" enabled={source.capabilities.references} />
                </div>
                
                <span className={`px-3 py-1 rounded-full text-sm ${
                  source.isActive 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {source.isActive ? 'Actif' : 'Inactif'}
                </span>
              </div>
            </div>
          ))}
          {sources && sources.length === 0 && (
            <p className="px-6 py-12 text-gray-500 text-center">
              Aucune source configurée
            </p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Informations</h2>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Version</h3>
            <p className="text-gray-600">OLS Bibliographie v1.0.0</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-700">API Backend</h3>
            <p className="text-gray-600">http://localhost:8000</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Capability({ label, enabled }: { label: string; enabled: boolean }) {
  return (
    <div className="flex items-center gap-1">
      {enabled ? (
        <Check className="w-4 h-4 text-green-600" />
      ) : (
        <X className="w-4 h-4 text-gray-400" />
      )}
      <span className={enabled ? 'text-gray-700' : 'text-gray-400'}>{label}</span>
    </div>
  );
}
