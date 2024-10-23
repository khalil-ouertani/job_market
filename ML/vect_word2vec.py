from elasticsearch import Elasticsearch
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.preprocessing import normalize
import numpy as np
import nltk
import time

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

es = Elasticsearch(['http://es-container:9200'])

index_name = 'job_offers'

def wait_for_index(es, index_name):
    while not es.indices.exists(index=index_name):
        print(f"Waiting for index {index_name} to be available...")
        time.sleep(10)
    print(f"Index {index_name} is now available.")

wait_for_index(es, "job_offers")

# Récupérer les stopwords français
stop_words = set(stopwords.words('french'))

def get_job_descriptions(index_name):
    query = {
        "_source": ["id", "description"],  # Spécifie les champs que vous souhaitez récupérer
        "query": {
            "match_all": {}  # Récupérer toutes les offres
        },
        "size": 3000
    }

    # Requête ElasticSearch pour obtenir tous les documents
    response = es.search(index=index_name, body=query)  # Ajustez le paramètre 'size' si nécessaire

    # Extraire les résultats
    job_offers = []
    for hit in response['hits']['hits']:
        job_offer = {
            'id': hit['_id'],
            'description': hit['_source'].get('description', '')
        }
        job_offers.append(job_offer)

    return job_offers

# Récupérer les descriptions d'offres de travail
job_offers = get_job_descriptions(index_name)

# Tokenisation et suppression des stopwords
def preprocess_description(description):
    if description is None:
        return []
    tokens = word_tokenize(description.lower())
    tokens = [word for word in tokens if word.isalnum()]  # Garder seulement les mots alphanumériques
    tokens = [word for word in tokens if word not in stop_words]  # Supprimer les stopwords
    return tokens

# Prétraiter les descriptions pour Word2Vec
tokenized_descriptions = [preprocess_description(job['description']) for job in job_offers]

# Entraîner le modèle Word2Vec sur les descriptions tokenisées
model = Word2Vec(sentences=tokenized_descriptions, vector_size=100, window=5, min_count=1, workers=4)

# Enregistrer le modèle entraîné dans un fichier
model.save("/data/word2vec_model.model")
print("Modèle Word2Vec enregistré dans 'word2vec_model.model'.")

# Créer une représentation vectorielle de chaque description
def get_average_word2vec(tokens, model, vector_size):
    # Obtenir les vecteurs des mots présents dans le modèle Word2Vec
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    if vectors:
        # Calculer la moyenne des vecteurs de mots pour obtenir un vecteur de description
        return np.mean(vectors, axis=0)
    else:
        # Si aucun mot n'est dans le modèle, retourner un vecteur nul
        return np.zeros(vector_size)

# Appliquer la vectorisation Word2Vec sur les descriptions
vector_size = 100  # Doit être le même que 'vector_size' utilisé lors de l'entraînement du modèle
word2vec_documents = []
for idx, job_offer in enumerate(job_offers):
    word2vec_vector = get_average_word2vec(tokenized_descriptions[idx], model, vector_size)
    word2vec_vector = normalize([word2vec_vector])[0].tolist()  # Normaliser le vecteur
    word2vec_documents.append({
        "id": job_offer['id'],
        "description_vector": word2vec_vector
    })

# Créer un nouvel index pour les vecteurs Word2Vec dans Elasticsearch
index_word2vec = 'job_offers_word2vec'

# Vérifier si le nouvel index existe, sinon le créer
if es.indices.exists(index=index_word2vec):
    es.indices.delete(index=index_word2vec)
    es.indices.create(index=index_word2vec)
else:
    es.indices.create(index=index_word2vec)

# Charger les documents avec vecteurs Word2Vec dans Elasticsearch
for doc in word2vec_documents:
    es.index(index=index_word2vec, id=doc["id"], body={"description_vector": doc["description_vector"]})

print(f"Chargement des vecteurs Word2Vec avec suppression des stopwords dans l'index '{index_word2vec}' terminé.")
