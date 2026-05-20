import re
import nltk
from nltk.corpus import stopwords

# S'assurer que les stopwords sont téléchargés
try:
    stopwords.words('french')
except LookupError:
    nltk.download('stopwords')

def nettoyer_texte(texte):
    """
    Prendre un texte en entrée, le mettre en minuscules, le tokenizer (supprimer la ponctuation),
    et retirer les mots vides français.
    Retourner une liste de mots-clés.
    """
    if not texte:
        return []
        
    # Mise en minuscules
    texte = texte.lower()
    
    # Tokenisation rudimentaire par regex (mots de 2 caractères et plus)
    mots = re.findall(r'\b[a-zàâäéèêëîïôöùûüç]{2,}\b', texte)
    
    # Suppression des stop words
    stop_words_fr = set(stopwords.words('french'))
    
    # Ajout de quelques stop words personnalisés souvent rencontrés dans l'actualité
    stop_words_perso = {'plus', 'cette', 'fait', 'faire', 'tout', 'tous', 'être', 'avoir', 'comme', 'aussi'}
    stop_words_fr.update(stop_words_perso)
    
    mots_cles = [mot for mot in mots if mot not in stop_words_fr]
    
    return mots_cles

if __name__ == "__main__":
    test_texte = "Ceci est un test de la fonction de nettoyage du texte, avec quelques mots en plus !"
    print(nettoyer_texte(test_texte))
