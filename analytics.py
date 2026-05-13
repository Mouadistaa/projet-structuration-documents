from collections import Counter
from nlp_utils import nettoyer_texte
import pymongo

def obtenir_frequence_mots(db, filtres):
    """
    Récupérer les articles correspondant aux filtres et calculer la fréquence
    de chaque mot clé.
    """
    articles = db.rechercher_articles(filtres)
    
    compteur = Counter()
    for article in articles:
        # Utilisation des mots clés déjà stockés pour la performance, 
        # mais s'il est nécessaire de refaire le passage NLP, il est possible d'utiliser nettoyer_texte(article['titre'])
        mots = article.get('mots_cles', [])
        if not mots:
            mots = nettoyer_texte(article.get('titre', ''))
            
        compteur.update(mots)
        
    # Retourner un dictionnaire {mot: nombre}
    return dict(compteur)

def obtenir_frequence_mots_agregation(db, filtres):
    """
    Version optimisée utilisant le pipeline d'agrégation de MongoDB.
    Plus performant pour de gros volumes de données.
    """
    if db.articles is None:
        return {}
        
    pipeline = [
        {"$match": filtres},
        {"$unwind": "$mots_cles"},
        {"$group": {"_id": "$mots_cles", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    try:
        resultats = db.articles.aggregate(pipeline)
        return {doc["_id"]: doc["count"] for doc in resultats}
    except Exception as e:
        print(f"Erreur d'agrégation : {e}")
        return {}

if __name__ == "__main__":
    from BdMongo import BdMongo
    db = BdMongo()
    freq = obtenir_frequence_mots_agregation(db, {})
    print("Top 10 mots :", list(freq.items())[:10])
