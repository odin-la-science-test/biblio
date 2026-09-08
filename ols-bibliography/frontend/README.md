# OLS Bibliographie - Frontend

Interface utilisateur React/TypeScript pour le module de bibliographie scientifique OLS.

## Fonctionnalités

- **Tableau de bord** : Vue d'ensemble des statistiques et documents
- **Recherche fédérée** : Recherche simultanée dans PubMed, OpenAlex, Crossref
- **Bibliothèques** : Gestion des bibliothèques personnelles et de laboratoire
- **Dossiers** : Organisation hiérarchique illimitée
- **Veilles** : Alertes automatiques sur les nouvelles publications
- **Tags** : Caractérisation transversale des documents

## Installation

```bash
npm install
```

## Développement

```bash
npm run dev
```

L'application sera disponible sur http://localhost:3000

## Build

```bash
npm run build
```

## Tests

```bash
npm run test
```

## Architecture

- **React 18** avec TypeScript
- **Vite** pour le build et le dev server
- **TailwindCSS** pour le styling
- **React Query** pour la gestion des données
- **React Router** pour la navigation
- **Axios** pour les requêtes API
- **Lucide React** pour les icônes
- **Vitest** + Testing Library pour les tests

## Structure

```
src/
├── components/     # Composants réutilisables
├── pages/         # Pages principales
├── services/      # Services API
├── hooks/         # Hooks personnalisés
├── types/         # Types TypeScript
├── utils/         # Utilitaires
└── test/          # Configuration des tests
```

## Connexion au Backend

Le frontend est configuré pour se connecter au backend FastAPI sur http://localhost:8000 via un proxy Vite.

Assurez-vous que le backend est démarré avant de lancer le frontend.
