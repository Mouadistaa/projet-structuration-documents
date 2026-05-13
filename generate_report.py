from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

def generer_rapport(nom_fichier="rapport.pdf"):
    doc = SimpleDocTemplate(nom_fichier, pagesize=A4)
    styles = getSampleStyleSheet()
    Story = []
    
    # Styles personnalisés
    title_style = styles['Title']
    heading1 = styles['Heading1']
    heading2 = styles['Heading2']
    normal = styles['Normal']
    
    Story.append(Paragraph("Rapport Technique du Projet SD2026 : Nuage de Mots d'Actualité", title_style))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("1. Introduction", heading1))
    Story.append(Paragraph("Ce rapport détaille la conception et l'implémentation de l'application Flask d'analyse de sitemaps d'actualités et de génération de nuages de mots, répondant au mandat SD2026.", normal))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("2. Conception et Choix Techniques", heading1))
    
    Story.append(Paragraph("2.1. Base de données et Schéma MongoDB", heading2))
    texte_schema = (
        "MongoDB a été choisi pour sa flexibilité avec des données non structurées ou semi-structurées comme celles issues "
        "du web scraping. Le schéma principal est la collection 'articles' où chaque document représente un article "
        "d'actualité. Les champs choisis sont :<br/>"
        "- <b>titre</b> : Le titre de l'article extrait du XML.<br/>"
        "- <b>url_originale</b> : L'URL unique de l'article, utilisée comme identifiant fonctionnel.<br/>"
        "- <b>date_publication</b> : Date convertie en objet DateTime pour faciliter les requêtes temporelles.<br/>"
        "- <b>source_id</b> : L'identifiant de la source d'actualité (ex: 'lemonde').<br/>"
        "- <b>horodatage_consultation</b> : Date d'insertion/mise à jour dans notre système.<br/>"
        "- <b>mots_cles</b> : Un tableau de chaînes de caractères contenant les mots pertinents après passage dans le pipeline NLP (minuscules, tokenisation, suppression des stopwords)."
    )
    Story.append(Paragraph(texte_schema, normal))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("2.2. Stratégie d'Indexation", heading2))
    texte_index = (
        "Plusieurs index ont été mis en place pour optimiser de manière critique les performances :<br/>"
        "1. <b>Index unique sur 'url_originale'</b> : Cet index garantit qu'il n'y ait aucun doublon lors des multiples passes du scraper (upsert).<br/>"
        "2. <b>Index descendant sur 'date_publication'</b> : Crucial pour le filtrage par intervalle de temps, car les utilisateurs recherchent généralement les actualités récentes (ex: les 7 derniers jours).<br/>"
        "3. <b>Index ascendant sur 'source_id'</b> : Optimise les recherches spécifiques à une source.<br/>"
        "<b>Justification sur l'indexation des mots-clés :</b> Un index de type 'Text' MongoDB est idéal pour la recherche "
        "floue ou sémantique. Cependant, notre cas d'usage nécessite de calculer des fréquences exactes sur des tokens déjà normalisés et "
        "nettoyés en amont par NLP. Par conséquent, l'utilisation du pipeline `$match` sur le champ `mots_cles` (qui est un simple tableau de chaînes de caractères) "
        "est suffisante et plus légère pour des recherches exactes après pré-traitement, évitant ainsi la surcharge d'un index textuel global."
    )
    Story.append(Paragraph(texte_index, normal))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("2.3. Pipeline ETL (Ingestion Automatisée)", heading2))
    texte_etl = (
        "L'ingestion se fait de manière asynchrone grâce à APScheduler. Le script télécharge le sitemap, "
        "extrait les balises XML à l'aide de BeautifulSoup, puis applique directement la transformation NLP (NLTK) sur les titres. "
        "Stocker les mots-clés pré-calculés dans le tableau 'mots_cles' au moment de l'insertion permet un gain "
        "de performance massif lors des requêtes d'agrégation, évitant de retraiter le texte à chaque demande de l'utilisateur."
    )
    Story.append(Paragraph(texte_etl, normal))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("2.4. Logique Analytique et Pipeline d'Agrégation", heading2))
    texte_agreg = (
        "Pour compter la fréquence des mots, plutôt que de rapatrier tous les articles en mémoire Python, "
        "l'application délègue le travail à la base de données via le pipeline d'agrégation de MongoDB :<br/>"
        "- <b>$match</b> : Filtre les articles par source et/ou date.<br/>"
        "- <b>$unwind</b> : Déconstruit le tableau 'mots_cles' pour avoir un document par mot.<br/>"
        "- <b>$group</b> : Compte les occurrences de chaque mot ($sum: 1).<br/>"
        "- <b>$sort</b> : Trie les résultats de manière décroissante.<br/>"
        "Ce choix déplace la charge sur le serveur de base de données, qui est hautement optimisé pour ce type d'opération."
    )
    Story.append(Paragraph(texte_agreg, normal))
    Story.append(Spacer(1, 12))
    
    doc.build(Story)
    print(f"Rapport généré sous le nom : {nom_fichier}")

if __name__ == "__main__":
    generer_rapport()
