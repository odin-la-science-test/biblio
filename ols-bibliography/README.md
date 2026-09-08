# 📚 Module Bibliographie OLS (Odin La Science)

> Système complet de gestion bibliographique scientifique avec recherche fédérée, organisation intelligente et veille automatisée.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 Vue d'ensemble

Ce module implémente l'intégralité des spécifications techniques du système de bibliographie scientifique **Odin La Science (OLS)**. Il permet aux chercheurs de :

- 🔍 **Rechercher** dans multiples bases (PubMed, OpenAlex, Crossref) via une interface unifiée
- 📁 **Organiser** leurs documents dans des bibliothèques et dossiers hiérarchiques
- 🏷️ **Caractériser** avec un système de tags transversal
- 🔔 **Veiller** sur des sujets avec alertes automatiques
- 📊 **Analyser** via des statistiques contextuelles avancées

---

## 🏗️ Architecture du Système

### Diagramme d'Architecture Globale

```mermaid
graph TB
    subgraph Frontend ["🖥️ Frontend React/TypeScript"]
        UI[Interface Utilisateur]
        Pages[Pages: Dashboard, Recherche, Bibliothèques, Veilles]
        Components[Composants Réutilisables]
        State[Gestion d'État - React Query]
    end

    subgraph API["⚡ API Gateway - FastAPI"]
        Router[Routeur API REST]
        Auth[Authentification JWT]
        Val[Validation Pydantic]
    end

    subgraph Backend["🔧 Backend Services"]
        DocService[Service Documents]
        SearchService[Service Recherche Fédérée]
        LibService[Service Bibliothèques]
        WatchService[Service Veilles]
        StatsService[Service Statistiques]
    end

    subgraph Connectors["🌐 Connecteurs Externes"]
        PubMed[PubMed API]
        OpenAlex[OpenAlex API]
        Crossref[Crossref API]
    end

    subgraph Data["💾 Couche Données"]
        PostgreSQL[(PostgreSQL)]
        Cache[(Redis Cache)]
    end

    UI --> Pages
    Pages --> Components
    Components --> State
    State --> Router
    Router --> Auth
    Auth --> Val
    Val --> DocService
    Val --> SearchService
    Val --> LibService
    Val --> WatchService
    Val --> StatsService
    
    SearchService --> PubMed
    SearchService --> OpenAlex
    SearchService --> Crossref
    
    DocService --> PostgreSQL
    LibService --> PostgreSQL
    WatchService --> PostgreSQL
    StatsService --> PostgreSQL
    SearchService --> Cache
```

### Flux de Recherche Fédérée

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant A as API FastAPI
    participant S as SearchService
    participant P as PubMed
    participant O as OpenAlex
    participant C as Crossref
    participant D as Database

    U->>F: Saisie requête + filtres
    F->>A: POST /api/search
    A->>S: execute_search(query, filters)
    
    S->>S: Analyser capacités sources
    S->>P: Requête adaptée PubMed
    S->>O: Requête adaptée OpenAlex
    S->>C: Requête adaptée Crossref
    
    P-->>S: Résultats bruts PubMed
    O-->>S: Résultats bruts OpenAlex
    C-->>S: Résultats bruts Crossref
    
    S->>S: Normalisation formats
    S->>S: Déduplication (DOI/PMID)
    S->>S: Calcul statistiques
    S->>D: Sauvegarde historique
    S-->>A: Résultats unifiés + stats
    A-->>F: JSON structuré
    F-->>U: Affichage résultats + facets
```

### Modèle de Données Canonique

```mermaid
erDiagram
    CanonicalDocument ||--o{ DocumentSource : "a plusieurs versions"
    CanonicalDocument ||--o{ LibraryDocument : "dans plusieurs bibliothèques"
    CanonicalDocument ||--o{ FolderDocument : "dans plusieurs dossiers"
    CanonicalDocument ||--o{ TagDocument : "taggué plusieurs fois"
    
    Library ||--o{ LibraryDocument : "contient"
    Library ||--o{ UserLibrary : "appartient à"
    
    Folder ||--o{ FolderDocument : "contient"
    Folder ||--o{ Folder : "parent/enfant"
    
    Tag ||--o{ TagDocument : "associe"
    
    User ||--o{ Library : "crée"
    User ||--o{ Folder : "crée"
    User ||--o{ Tag : "crée"
    User ||--o{ SavedSearch : "crée"
    User ||--o{ Watch : "crée"
    
    SavedSearch ||--o{ Watch : "déclenche"
    
    CanonicalDocument {
        uuid id PK
        string title
        string abstract
        string doi UK
        string pmid UK
        date publication_date
        json metadata
        datetime created_at
        datetime updated_at
    }
    
    DocumentSource {
        uuid id PK
        uuid canonical_id FK
        string source_name
        string source_id
        json raw_data
        datetime fetched_at
    }
    
    Library {
        uuid id PK
        string name
        string type
        uuid owner_id FK
        datetime created_at
    }
    
    Folder {
        uuid id PK
        uuid parent_id FK
        string name
        uuid owner_id FK
    }
    
    Tag {
        uuid id PK
        string name
        string color
        uuid owner_id FK
    }
    
    Watch {
        uuid id PK
        string name
        uuid saved_search_id FK
        string frequency
        boolean active
        datetime last_run
    }
```

---

## 📂 Structure du Projet

```
ols-bibliography/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── config.py            # Configuration environnement
│   │   ├── database.py          # Connexion PostgreSQL async
│   │   ├── models/              # Modèles SQLAlchemy (14 entités)
│   │   │   └── __init__.py
│   │   ├── schemas/             # Schémas Pydantic (40+ types)
│   │   │   └── __init__.py
│   │   ├── routers/             # Routes API REST
│   │   │   └── __init__.py
│   │   └── services/            # Logique métier
│   │       └── search_service.py
│   ├── tests/
│   │   ├── test_api.py          # Tests endpoints API
│   │   ├── test_services.py     # Tests logique métier
│   │   └── conftest.py          # Fixtures pytest
│   ├── requirements.txt
│   ├── pytest.ini
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Composants réutilisables
│   │   │   ├── ui/              # Base UI (boutons, inputs)
│   │   │   ├── documents/       # Composants documents
│   │   │   ├── libraries/       # Composants bibliothèques
│   │   │   └── search/          # Composants recherche
│   │   ├── pages/               # Pages principales
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Search.tsx
│   │   │   ├── Libraries.tsx
│   │   │   ├── Watches.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # Appels API
│   │   ├── types/               # Types TypeScript
│   │   ├── utils/               # Fonctions utilitaires
│   │   └── App.tsx
│   ├── public/
│   ├── tests/                   # Tests Vitest
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docker-compose.yml           # Orchestration containers
├── .env.example                 # Variables d'environnement
└── README.md                    # Ce fichier
```

---

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optionnel)

### Option 1 : Avec Docker (Recommandé)

```bash
# Cloner le dépôt
git clone <repository-url>
cd ols-bibliography

# Lancer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

Accès :
- Frontend : http://localhost:3000
- API Swagger : http://localhost:8000/docs
- PostgreSQL : localhost:5432

### Option 2 : Manuellement

#### Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Configurer variables d'environnement
cp ../.env.example .env
# Éditer .env avec vos paramètres DB

# Lancer migrations (si Alembic configuré)
# alembic upgrade head

# Démarrer serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Installer dépendances
npm install

# Copier configuration
cp .env.example .env.local

# Démarrer développement
npm run dev

# Build production
npm run build

# Lancer tests
npm run test
```

---

## 📡 API Reference

### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/documents` | Liste documents paginée |
| `POST` | `/api/documents` | Créer document |
| `GET` | `/api/documents/{id}` | Détails document |
| `PUT` | `/api/documents/{id}` | Mettre à jour |
| `DELETE` | `/api/documents/{id}` | Supprimer |
| `POST` | `/api/search` | Recherche fédérée |
| `GET` | `/api/libraries` | Liste bibliothèques |
| `POST` | `/api/libraries` | Créer bibliothèque |
| `GET` | `/api/folders` | Arborescence dossiers |
| `POST` | `/api/tags` | Créer tag |
| `GET` | `/api/watches` | Liste veilles |
| `POST` | `/api/watches` | Créer veille |
| `GET` | `/api/statistics` | Statistiques contextuelles |

### Exemple de Requête Recherche

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "machine learning cancer",
    "filters": {
      "publication_date_min": "2023-01-01",
      "document_types": ["journal-article"],
      "sources": ["pubmed", "openalex"]
    },
    "pagination": {
      "page": 1,
      "page_size": 20
    }
  }'
```

### Exemple de Réponse

```json
{
  "results": [
    {
      "canonical_id": "uuid-123",
      "title": "Deep Learning for Cancer Detection",
      "abstract": "...",
      "doi": "10.1234/example",
      "pmid": "12345678",
      "publication_date": "2023-06-15",
      "authors": ["Dupont J.", "Martin L."],
      "sources": [
        {
          "name": "pubmed",
          "source_id": "12345678",
          "url": "https://pubmed.ncbi.nlm.nih.gov/12345678"
        }
      ],
      "metrics": {
        "citation_count": 42,
        "relevance_score": 0.95
      }
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20,
  "statistics": {
    "by_year": {"2023": 89, "2022": 45, "2021": 22},
    "by_type": {"journal-article": 120, "conference": 36},
    "by_source": {"pubmed": 98, "openalex": 58}
  }
}
```

---

## 🧪 Tests

### Backend (pytest)

```bash
cd backend
source venv/bin/activate

# Tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_api.py::test_search_endpoint -v
```

### Frontend (Vitest)

```bash
cd frontend

# Tous les tests
npm run test

# Mode watch
npm run test:watch

# Avec couverture
npm run test:coverage
```

### Couverture de Code Objectif

- Backend : > 85%
- Frontend : > 80%
- Critique (search, dedup) : > 95%

---

## 🔧 Configuration

### Variables d'Environnement

#### Backend (.env)

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ols_bibliography

# Redis (cache)
REDIS_URL=redis://localhost:6379/0

# API Keys (optionnel selon sources)
PUBMED_API_KEY=votre_cle_pubmed
OPENALEX_MAILTO=votre@email.com

# JWT
JWT_SECRET=votre_secret_jwt
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Logging
LOG_LEVEL=INFO
```

#### Frontend (.env.local)

```ini
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME="Bibliographie OLS"
VITE_ENABLE_DEBUG=true
```

---

## 📊 Fonctionnalités Détaillées

### 1. Recherche Fédérée Intelligente

Le système adapte automatiquement les requêtes selon les capacités de chaque source :

| Source | Filtres supportés | Tri disponible | Pagination |
|--------|------------------|----------------|------------|
| PubMed | Date, type, texte | Pertinence, date | Oui (MAX 10k) |
| OpenAlex | Date, auteur, inst. | Citations, date | Oui (illimité) |
| Crossref | DOI, titre, ISSN | Pertinence | Oui |

**Algorithme de déduplication :**
1. Regroupement par DOI (prioritaire)
2. Regroupement par PMID si DOI absent
3. Fuzzy matching titre + auteurs + année
4. Conservation métadonnées les plus complètes

### 2. Organisation Hiérarchique

- **Bibliothèques** : Conteneurs principaux (perso, labo, projet)
- **Dossiers** : Arborescence illimitée (glisser-déposer)
- **Tags** : Caractérisation transversale multi-couleurs
- **Vues dynamiques** : Combinaison dossiers + tags + filtres

### 3. Système de Veille Automatisé

Création de veilles basées sur :
- Requêtes sauvegardées
- Fréquence d'exécution (quotidien, hebdo, mensuel)
- Canaux de notification (email, dashboard, webhook)
- Historique des alertes déclenchées

### 4. Statistiques Contextuelles

Calcul en temps réel de :
- Distribution temporelle (par année/mois)
- Types de documents (article, conférence, thèse)
- Sources utilisées
- Auteurs/productivité
- Journaux dominants
- Tendances émergentes

---

## 🛠️ Stack Technique

### Backend
- **Framework** : FastAPI 0.100+
- **Langage** : Python 3.10+
- **ORM** : SQLAlchemy 2.0 (async)
- **Validation** : Pydantic v2
- **Base de données** : PostgreSQL 14+
- **Cache** : Redis
- **Tests** : pytest + httpx
- **Documentation** : OpenAPI 3.0 (Swagger)

### Frontend
- **Framework** : React 18+
- **Langage** : TypeScript 5+
- **Build** : Vite
- **Style** : TailwindCSS 3+
- **État** : React Query + Zustand
- **Tests** : Vitest + React Testing Library
- **Routing** : React Router v6

### DevOps
- **Containerisation** : Docker + Docker Compose
- **CI/CD** : GitHub Actions (à configurer)
- **Monitoring** : Prometheus + Grafana (optionnel)

---

## 🤝 Contribuer

1. Forker le projet
2. Créer une branche feature (`git checkout -b feature/amazing`)
3. Committer changements (`git commit -m 'Add amazing feature'`)
4. Pusher (`git push origin feature/amazing`)
5. Ouvrir Pull Request

### Guidelines de Code

- Backend : Respecter [PEP 8](https://pep8.org/) + type hints
- Frontend : ESLint + Prettier configurés
- Tests obligatoires pour nouvelles fonctionnalités
- Documentation API auto-générée (docstrings)

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE) pour détails.

---

## 📞 Support

- Documentation complète : `/docs`
- API Interactive : `http://localhost:8000/docs`
- Issues : GitHub Issues
- Email : support@odin-lascience.fr

---

## 🎨 Captures d'Écran

### Dashboard Principal
> Vue d'ensemble avec statistiques rapides, documents récents, veilles actives

### Interface de Recherche
> Barre de recherche unifiée, filtres facettes, résultats paginés, prévisualisation

### Gestion Bibliothèque
> Arborescence dossiers, drag-and-drop, tags colorés, métadonnées enrichies

### Configuration Veilles
> Créateur de requêtes sauvegardées, planning notifications, historique alertes

*(Les captures seront ajoutées après déploiement)*

---

## 🚀 Roadmap

- [ ] Intégration Zotero/Mendeley (import/export)
- [ ] IA : Suggestions de tags automatiques
- [ ] IA : Résumé automatique d'articles
- [ ] Collaboration temps réel (bibliothèques partagées)
- [ ] Plugin navigateur (capture web one-click)
- [ ] Application mobile (React Native)
- [ ] Export BibTeX/EndNote/RIS avancé
- [ ] Analyse de réseau de citations

---

**Développé avec ❤️ pour la communauté scientifique francophone**

*Projet Odin La Science - Module Bibliographie v1.0*
