import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchService } from '../services/api';
import type { Watch } from '../types';
import { Bell, Plus, Play, Trash2 } from 'lucide-react';

export default function Watches() {
  const [showNewWatch, setShowNewWatch] = useState(false);
  const [newWatch, setNewWatch] = useState({ name: '', query: '', frequency: 'weekly' as const });
  const queryClient = useQueryClient();

  const { data: watches, isLoading } = useQuery({
    queryKey: ['watches'],
    queryFn: async () => {
      try {
        const response = await watchService.getAll();
        return response.data;
      } catch (e) {
        return [];
      }
    }
  });

  const createWatch = useMutation({
    mutationFn: (data: any) => watchService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watches'] });
      setShowNewWatch(false);
      setNewWatch({ name: '', query: '', frequency: 'weekly' });
    }
  });

  const deleteWatch = useMutation({
    mutationFn: (id: string) => watchService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watches'] });
    }
  });

  const runWatch = useMutation({
    mutationFn: (id: string) => watchService.run(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watches'] });
    }
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newWatch.name.trim() && newWatch.query.trim()) {
      createWatch.mutate(newWatch);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Veilles documentaires</h1>
        <button
          onClick={() => setShowNewWatch(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nouvelle veille
        </button>
      </div>

      {showNewWatch && (
        <form onSubmit={handleCreate} className="bg-white p-4 rounded-lg shadow space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nom</label>
            <input
              type="text"
              value={newWatch.name}
              onChange={(e) => setNewWatch({...newWatch, name: e.target.value})}
              placeholder="Ex: IA en santé"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Requête</label>
            <textarea
              value={newWatch.query}
              onChange={(e) => setNewWatch({...newWatch, query: e.target.value})}
              placeholder="Ex: machine learning AND healthcare"
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fréquence</label>
            <select
              value={newWatch.frequency}
              onChange={(e) => setNewWatch({...newWatch, frequency: e.target.value as any})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="daily">Quotidien</option>
              <option value="weekly">Hebdomadaire</option>
              <option value="monthly">Mensuel</option>
            </select>
          </div>
          <div className="flex gap-4">
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Créer
            </button>
            <button
              type="button"
              onClick={() => setShowNewWatch(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4">
        {watches && watches.map((watch: Watch) => (
          <div key={watch.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="bg-orange-100 p-2 rounded-lg">
                  <Bell className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{watch.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{watch.query}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>
                      Fréquence: {
                        watch.frequency === 'daily' ? 'Quotidien' :
                        watch.frequency === 'weekly' ? 'Hebdomadaire' : 'Mensuel'
                      }
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      watch.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {watch.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => runWatch.mutate(watch.id)}
                  disabled={runWatch.isPending}
                  className="p-2 text-gray-400 hover:text-indigo-600"
                  title="Exécuter maintenant"
                >
                  <Play className="w-5 h-5" />
                </button>
                <button
                  onClick={() => deleteWatch.mutate(watch.id)}
                  disabled={deleteWatch.isPending}
                  className="p-2 text-gray-400 hover:text-red-600"
                  title="Supprimer"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
        {watches && watches.length === 0 && (
          <p className="text-gray-500 text-center py-12">
            Aucune veille configurée. Créez votre première veille !
          </p>
        )}
      </div>
    </div>
  );
}
