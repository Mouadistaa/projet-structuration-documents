# Nuage de Mots d'Actualité

Projet de groupe — Master MIAGE, Structuration de Documents

**Équipe** : FUMERON–LECOMTE Baptiste, EL AOUDI Rim, SAHRAOUI DOUKKALI Mouad, KACHLER Théo

## Prérequis

- Python 3.8 ou supérieur
- MongoDB Community Server (en cours d'exécution sur `localhost:27017`)
- pip

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/Mouadistaa/projet-structuration-documents.git
cd projet-structuration-documents

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Lancer MongoDB

MongoDB doit tourner sur `localhost:27017` sans authentification.

```bash
# Linux/Mac
mongod

# Windows (si installé en service, il tourne déjà)
# Sinon, lancer mongod.exe depuis le dossier d'installation
```

## Lancer l'application

```bash
python main.py
```

L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

Au premier lancement, la source « Le Monde » est ajoutée automatiquement et la collecte des articles démarre.

## Utilisation

### Mode Administration (`/admin`)

- Ajouter un abonnement : saisir un identifiant (ex : `lefigaro`) et l'URL du sitemap (ex : `https://www.lefigaro.fr/sitemap_news.xml`)
- Supprimer un abonnement
- Forcer la collecte manuellement

### Mode Consultation (`/articles`)

- Parcourir les articles collectés
- Filtrer par source, période, ou mot-clé
- Cliquer sur un titre pour lire l'article (ouverture dans un nouvel onglet, la consultation est enregistrée)

### Nuage de Mots (`/`)

- Choisir une source (ou toutes), une période, et le nombre de mots souhaités
- Générer et visualiser le nuage
- Télécharger le SVG

## Structure du projet

```
├── main.py              # Point d'entrée Flask (routes)
├── BdMongo.py           # Couche d'accès à MongoDB
├── pipeline.py          # Collecte et parsing des sitemaps XML
├── analytics.py         # Pipeline d'agrégation (fréquences)
├── nlp_utils.py         # Nettoyage de texte / stop-words
├── requirements.txt     # Dépendances Python
├── static/
│   └── style.css        # Feuille de style
├── templates/
│   ├── base.html        # Template de base (navbar, layout)
│   ├── index.html       # Page d'accueil (nuage de mots)
│   ├── articles.html    # Page de consultation
│   └── admin.html       # Page d'administration
└── rapport.pdf          # Rapport de projet
```

## Base de données

- Nom : `SD2026_projet`
- Collections : `G_FKES_sources`, `G_FKES_articles`
- Connexion : `mongodb://localhost:27017` (sans authentification)

## Dépendances principales

- Flask (micro-framework web)
- PyMongo (driver MongoDB)
- NLTK (stop-words français)
- wordcloud (génération du nuage de mots)
- APScheduler (collecte automatique périodique)