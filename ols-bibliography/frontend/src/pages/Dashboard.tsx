import { useQuery } from '@tanstack/react-query';
import { statisticsService } from '../services/api';
import type { Statistics } from '../types';
import { BookOpen, Search, Bell, Folder } from 'lucide-react';

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      try {
        const response = await statisticsService.getOverview();
        return response.data;
      } catch (e) {
        return null;
      }
    }
  });

  const stats: Partial<Statistics> = data || {
    totalDocuments: 0,
    documentsByYear: {},
    documentsBySource: {},
    topAuthors: []
  };

  if (error) {
    return <div className="p-4 text-red-600">Erreur de chargement des statistiques</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={BookOpen}
          title="Documents"
          value={stats.totalDocuments?.toString() || '0'}
          color="bg-blue-500"
        />
        <StatCard 
          icon={Folder}
          title="Bibliothèques"
          value="3"
          color="bg-green-500"
        />
        <StatCard 
          icon={Search}
          title="Recherches sauvegardées"
          value="5"
          color="bg-purple-500"
        />
        <StatCard 
          icon={Bell}
          title="Veilles actives"
          value="2"
          color="bg-orange-500"
        />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Documents par année</h2>
        {stats.documentsByYear && Object.keys(stats.documentsByYear).length > 0 ? (
          <div className="h-64 flex items-end space-x-2">
            {Object.entries(stats.documentsByYear)
              .sort(([a], [b]) => a.localeCompare(b))
              .slice(-10)
              .map(([year, count]) => (
                <div key={year} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-indigo-500 rounded-t"
                    style={{ height: `${(count / Math.max(...Object.values(stats.documentsByYear!))) * 200}px` }}
                  />
                  <span className="text-xs text-gray-600 mt-2">{year}</span>
                </div>
              ))}
          </div>
        ) : (
          <p className="text-gray-500">Aucune donnée disponible</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Top auteurs</h2>
        {stats.topAuthors && stats.topAuthors.length > 0 ? (
          <ul className="space-y-2">
            {stats.topAuthors.slice(0, 5).map((author, idx) => (
              <li key={idx} className="flex justify-between items-center py-2 border-b">
                <span className="font-medium">{author.name}</span>
                <span className="text-gray-500">{author.count} documents</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">Aucun auteur trouvé</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, color }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6 flex items-center space-x-4">
      <div className={`${color} p-3 rounded-lg`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  );
}
