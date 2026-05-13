import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime

class BdMongo:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="SD2026_projet"):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.articles = None
        self.sources = None
        self.connect()
        self.setup_indexes()

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.articles = self.db.articles
            self.sources = self.db.sources
            print("Connexion MongoDB réussie.")
        except ConnectionFailure:
            print("Erreur : Impossible de se connecter à MongoDB.")

    def setup_indexes(self):
        if self.articles is not None:
            # Index pour des requêtes rapides basées sur le temps et la source
            self.articles.create_index([("date_publication", pymongo.DESCENDING)])
            self.articles.create_index([("source_id", pymongo.ASCENDING)])
            # Optionnel : Index composé si les requêtes combinent souvent les deux
            self.articles.create_index([("source_id", pymongo.ASCENDING), ("date_publication", pymongo.DESCENDING)])
            # Index unique pour éviter les doublons
            self.articles.create_index([("url_originale", pymongo.ASCENDING)], unique=True)
            print("Index MongoDB configurés.")

    def inserer_article(self, article_data):
        """
        Insérer un article s'il n'existe pas déjà.
        """
        if self.articles is None:
            print("Erreur : Pas de connexion à la base de données.")
            return False
            
        article_data['horodatage_consultation'] = datetime.utcnow()
        try:
            # Utilisation de update_one avec upsert pour éviter les doublons et gérer l'index unique
            result = self.articles.update_one(
                {"url_originale": article_data["url_originale"]},
                {"$setOnInsert": article_data},
                upsert=True
            )
            return result.upserted_id is not None
        except Exception as e:
            print(f"Erreur d'insertion: {e}")
            return False

    def rechercher_articles(self, filtres):
        """
        Recherche des articles en fonction de filtres.
        filtres: dict (ex: {"source_id": "lemonde", "date_publication": {"$gte": date_debut, "$lte": date_fin}})
        """
        if self.articles is None:
            return []
        return list(self.articles.find(filtres))

    def mettre_a_jour_horodatage(self, url_originale):
        if self.articles is None:
            return
        try:
            self.articles.update_one(
                {"url_originale": url_originale},
                {"$set": {"horodatage_consultation": datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Erreur de mise à jour: {e}")

    # --- Gestion des sources ---
    def inserer_source(self, url_sitemap, source_id, frequence_heures=6):
        if self.sources is None:
            print("Erreur : Pas de connexion à la base de données.")
            return False
        try:
            self.sources.update_one(
                {"source_id": source_id},
                {"$set": {"url_sitemap": url_sitemap, "frequence_heures": frequence_heures}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Erreur d'insertion de source: {e}")
            return False
            
    def supprimer_source(self, source_id):
        if self.sources is None or self.articles is None:
            return
        self.sources.delete_one({"source_id": source_id})
        # Optionnel : supprimer tous les articles de cette source
        self.articles.delete_many({"source_id": source_id})

    def obtenir_sources(self):
        if self.sources is None:
            return []
        return list(self.sources.find())

if __name__ == "__main__":
    db = BdMongo()
