import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryService, folderService } from '../services/api';
import type { Library, Folder } from '../types';
import { useState } from 'react';
import { Folder as FolderIcon, Plus, MoreVertical } from 'lucide-react';

export default function Libraries() {
  const [showNewLibrary, setShowNewLibrary] = useState(false);
  const [newLibraryName, setNewLibraryName] = useState('');
  const queryClient = useQueryClient();

  const { data: libraries, isLoading } = useQuery({
    queryKey: ['libraries'],
    queryFn: async () => {
      try {
        const response = await libraryService.getAll();
        return response.data;
      } catch (e) {
        return [];
      }
    }
  });

  const createLibrary = useMutation({
    mutationFn: (name: string) => libraryService.create({ name, isPersonal: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      setShowNewLibrary(false);
      setNewLibraryName('');
    }
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newLibraryName.trim()) {
      createLibrary.mutate(newLibraryName);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Bibliothèques</h1>
        <button
          onClick={() => setShowNewLibrary(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nouvelle bibliothèque
        </button>
      </div>

      {showNewLibrary && (
        <form onSubmit={handleCreate} className="bg-white p-4 rounded-lg shadow">
          <div className="flex gap-4">
            <input
              type="text"
              value={newLibraryName}
              onChange={(e) => setNewLibraryName(e.target.value)}
              placeholder="Nom de la bibliothèque"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Créer
            </button>
            <button
              type="button"
              onClick={() => setShowNewLibrary(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {libraries && libraries.map((library: Library) => (
          <LibraryCard key={library.id} library={library} />
        ))}
        {libraries && libraries.length === 0 && (
          <p className="col-span-full text-gray-500 text-center py-12">
            Aucune bibliothèque. Créez votre première bibliothèque !
          </p>
        )}
      </div>
    </div>
  );
}

function LibraryCard({ library }: { library: Library }) {
  const { data: folders } = useQuery({
    queryKey: ['folders', library.id],
    queryFn: async () => {
      try {
        const response = await folderService.getAll(library.id);
        return response.data;
      } catch (e) {
        return [];
      }
    }
  });

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 p-2 rounded-lg">
              <FolderIcon className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{library.name}</h3>
              <p className="text-sm text-gray-500">
                {library.isPersonal ? 'Personnelle' : 'Laboratoire'}
              </p>
            </div>
          </div>
          <button className="text-gray-400 hover:text-gray-600">
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>
        
        {library.description && (
          <p className="text-sm text-gray-600 mb-4">{library.description}</p>
        )}
        
        <div className="text-sm text-gray-500">
          {folders && folders.length > 0 ? (
            <span>{folders.length} dossier(s)</span>
          ) : (
            <span>Aucun dossier</span>
          )}
        </div>
      </div>
      
      <div className="px-6 py-3 bg-gray-50 border-t rounded-b-lg">
        <button className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
          Voir les documents →
        </button>
      </div>
    </div>
  );
}
