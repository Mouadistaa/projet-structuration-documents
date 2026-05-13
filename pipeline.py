import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from BdMongo import BdMongo
from nlp_utils import nettoyer_texte
import time

def parse_date(date_str):
    try:
        # Essayer d'analyser le format ISO standard couramment utilisé dans les sitemaps
        # Exemple : 2026-04-26T15:52:37+02:00
        # Suppression des deux-points dans le fuseau horaire pour strptime
        if '+' in date_str:
            date_str = date_str.rsplit('+', 1)[0]
        return datetime.fromisoformat(date_str)
    except Exception as e:
        print(f"Erreur de parsing de date {date_str}: {e}")
        return datetime.utcnow()

def scraper_source(db, url_sitemap, source_id):
    print(f"[{datetime.now()}] Début du scraping pour {source_id} ({url_sitemap})")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_sitemap, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsing XML direct avec ElementTree
        root = ET.fromstring(response.content)
        
        # Les sitemaps utilisent un namespace, il est nécessaire de le gérer
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
              'news': 'http://www.google.com/schemas/sitemap-news/0.9'}
              
        urls = root.findall('sitemap:url', ns)
        
        nouveaux_articles = 0
        
        for url_tag in urls:
            loc_tag = url_tag.find('sitemap:loc', ns)
            if loc_tag is None:
                continue
            
            url_originale = loc_tag.text
            
            news_tag = url_tag.find('news:news', ns)
            if news_tag is None:
                continue
                
            title_tag = news_tag.find('news:title', ns)
            date_tag = news_tag.find('news:publication_date', ns)
            
            if title_tag is None or date_tag is None:
                continue
                
            titre = title_tag.text
            date_publication = parse_date(date_tag.text)
            
            # Application du NLP sur le titre
            mots_cles = nettoyer_texte(titre)
            
            article_data = {
                "titre": titre,
                "url_originale": url_originale,
                "date_publication": date_publication,
                "source_id": source_id,
                "mots_cles": mots_cles
            }
            
            insere = db.inserer_article(article_data)
            if insere:
                nouveaux_articles += 1
                
        print(f"[{datetime.now()}] Fin du scraping pour {source_id}. {nouveaux_articles} nouveaux articles insérés.")
        
    except requests.RequestException as e:
        print(f"Erreur de requête pour {url_sitemap}: {e}")
    except Exception as e:
        print(f"Erreur générale lors du scraping de {url_sitemap}: {e}")

def executer_pipeline_complet(db):
    sources = db.obtenir_sources()
    for source in sources:
        scraper_source(db, source['url_sitemap'], source['source_id'])

# Point d'entrée pour tester le pipeline individuellement
if __name__ == "__main__":
    db = BdMongo()
    # Ajout d'une source de test si elle n'existe pas
    db.inserer_source("https://www.lemonde.fr/sitemap_news.xml", "lemonde", 6)
    executer_pipeline_complet(db)
