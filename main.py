from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from BdMongo import BdMongo
from analytics import obtenir_frequence_mots_agregation
from pipeline import executer_pipeline_complet
from apscheduler.schedulers.background import BackgroundScheduler
import wordcloud
from datetime import datetime, timedelta

app = Flask(__name__)
db = BdMongo()

# Configuration du planificateur
scheduler = BackgroundScheduler()
# Par défaut, le pipeline est lancé toutes les 6 heures
job = scheduler.add_job(func=executer_pipeline_complet, args=[db], trigger="interval", hours=6, id="pipeline_job")
scheduler.start()

# S'assurer qu'il s'arrête à la fermeture
import atexit
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    sources = db.obtenir_sources()
    return render_template('index.html', sources=sources)

@app.route('/api/wordcloud')
def api_wordcloud():
    try:
        source_id = request.args.get('source_id')
        jours = request.args.get('jours', type=int, default=7)
        max_mots = request.args.get('max_mots', type=int, default=100)
        
        filtres = {}
        if source_id:
            filtres['source_id'] = source_id
            
        date_limite = datetime.utcnow() - timedelta(days=jours)
        filtres['date_publication'] = {"$gte": date_limite}
        
        freq = obtenir_frequence_mots_agregation(db, filtres)
        
        if not freq:
            if db.articles is None:
                msg = "Erreur: MongoDB n'est pas connecté"
            else:
                msg = "Aucune donnée trouvée"
            return f"<svg viewBox='0 0 800 400' width='100%' height='100%' xmlns='http://www.w3.org/2000/svg'><text x='400' y='200' font-family='sans-serif' font-size='24' text-anchor='middle' fill='#94a3b8'>{msg}</text></svg>"
            
        # Limiter au max_mots
        freq = dict(list(freq.items())[:max_mots])
        
        wc = wordcloud.WordCloud(width=800, height=400, background_color='white', mode='RGBA')
        wc.generate_from_frequencies(freq)
        svg_data = wc.to_svg()
        
        # Rendre le SVG responsive
        svg_data = svg_data.replace('width="800" height="400"', 'viewBox="0 0 800 400" width="100%" height="100%"')
        
        return Response(svg_data, mimetype='image/svg+xml')
    except Exception as e:
        print(f"Erreur API wordcloud: {e}")
        return f"<svg viewBox='0 0 800 400' width='100%' height='100%' xmlns='http://www.w3.org/2000/svg'><text x='400' y='200' font-family='sans-serif' fill='red' text-anchor='middle'>Erreur: {str(e)[:50]}</text></svg>", 500

@app.route('/download/wordcloud.svg')
def download_wordcloud():
    try:
        source_id = request.args.get('source_id')
        jours = request.args.get('jours', type=int, default=7)
        max_mots = request.args.get('max_mots', type=int, default=100)
        
        filtres = {}
        if source_id:
            filtres['source_id'] = source_id
            
        date_limite = datetime.utcnow() - timedelta(days=jours)
        filtres['date_publication'] = {"$gte": date_limite}
        
        freq = obtenir_frequence_mots_agregation(db, filtres)
        
        if not freq:
            return "Aucune donnée trouvée", 404
            
        freq = dict(list(freq.items())[:max_mots])
        
        wc = wordcloud.WordCloud(width=800, height=400, background_color='white', mode='RGBA')
        wc.generate_from_frequencies(freq)
        svg_data = wc.to_svg()
        
        return Response(
            svg_data,
            mimetype="image/svg+xml",
            headers={"Content-disposition": "attachment; filename=nuage_mots.svg"}
        )
    except Exception as e:
        print(f"Erreur Download wordcloud: {e}")
        return "Erreur interne lors de la génération", 500

@app.route('/articles')
def articles():
    source_id = request.args.get('source_id')
    jours = request.args.get('jours', type=int, default=30)
    mot_cle = request.args.get('mot_cle', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    filtres = {}
    if source_id:
        filtres['source_id'] = source_id
        
    if jours > 0:
        date_limite = datetime.utcnow() - timedelta(days=jours)
        filtres['date_publication'] = {"$gte": date_limite}
        
    if mot_cle:
        # Recherche insensible à la casse dans les mots clés
        filtres['mots_cles'] = {"$regex": mot_cle, "$options": "i"}
        
    total_articles = db.compter_articles(filtres)
    total_pages = (total_articles + per_page - 1) // per_page
    
    if page < 1:
        page = 1
        
    liste_articles = db.rechercher_articles(
        filtres, 
        tri=[("date_publication", -1)], 
        skip=(page - 1) * per_page, 
        limit=per_page
    )
    
    populaires = db.obtenir_articles_populaires(limite=5)
    sources = db.obtenir_sources()
    
    return render_template('articles.html', 
                           articles=liste_articles, 
                           sources=sources, 
                           populaires=populaires, 
                           args=request.args,
                           page=page,
                           total_pages=total_pages,
                           total_articles=total_articles)

@app.route('/goto')
def goto():
    url = request.args.get('url')
    if not url:
        return redirect(url_for('articles'))
        
    # Mettre à jour l'horodatage de consultation dans la base de données
    db.mettre_a_jour_horodatage(url)
    
    # Rediriger vers la page d'origine de l'article dans un nouvel onglet (géré par le front)
    return redirect(url)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'ajouter':
            url_sitemap = request.form.get('url_sitemap')
            source_id = request.form.get('source_id')
            db.inserer_source(url_sitemap, source_id)
        elif action == 'supprimer':
            source_id = request.form.get('source_id')
            db.supprimer_source(source_id)
        elif action == 'forcer_collecte':
            executer_pipeline_complet(db)
        elif action == 'modifier_planification':
            jours = int(request.form.get('jours', 0))
            heures = int(request.form.get('heures', 6))
            if jours == 0 and heures == 0:
                heures = 1
            scheduler.reschedule_job('pipeline_job', trigger='interval', days=jours, hours=heures)
            
        return redirect(url_for('admin'))
        
    sources = db.obtenir_sources()
    
    current_jours = 0
    current_heures = 6
    job = scheduler.get_job('pipeline_job')
    if job and hasattr(job.trigger, 'interval'):
        total_seconds = job.trigger.interval.total_seconds()
        current_jours = int(total_seconds // 86400)
        current_heures = int((total_seconds % 86400) // 3600)
        
    return render_template('admin.html', sources=sources, current_jours=current_jours, current_heures=current_heures)

if __name__ == '__main__':
    # Initialisation optionnelle de base si vide
    if not db.obtenir_sources():
        db.inserer_source("https://www.lemonde.fr/sitemap_news.xml", "lemonde", 6)
        
    app.run(debug=True, use_reloader=False) # use_reloader=False pour éviter de lancer le planificateur deux fois
