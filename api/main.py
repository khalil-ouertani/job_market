from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from elasticsearch import Elasticsearch, NotFoundError
from gensim.models import Word2Vec
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle
import os

# Téléchargement des ressources NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Initialisation
es = Elasticsearch(['http://es-container:9200'])

app = FastAPI()

# Contexte de hash des mots de passe
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBasic()

# Récupérer les stopwords français
stop_words = set(stopwords.words('french'))

# Chemins vers les modèles sauvegardés
word2vec_model_path = "/data/word2vec_model.model"
tfidf_vectorizer_path = "/data/tfidf_vectorizer.pkl"

# Charger le modèle Word2Vec
if os.path.exists(word2vec_model_path):
    word2vec_model = Word2Vec.load(word2vec_model_path)
    print("Modèle Word2Vec chargé avec succès.")
else:
    print(f"Le modèle Word2Vec n'a pas été trouvé à l'emplacement {word2vec_model_path}.")

# Charger le vectoriseur TF-IDF
if os.path.exists(tfidf_vectorizer_path):
    with open(tfidf_vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    print("Vectoriseur TF-IDF chargé avec succès.")
else:
    print(f"Le vectoriseur TF-IDF n'a pas été trouvé à l'emplacement {tfidf_vectorizer_path}.")

# Fonction de prétraitement identique à celle de vos scripts
def preprocess_description(description):
    if description is None:
        return []
    tokens = word_tokenize(description.lower())
    tokens = [word for word in tokens if word.isalnum()]  # Garder seulement les mots alphanumériques
    tokens = [word for word in tokens if word not in stop_words]  # Supprimer les stopwords
    return tokens

# Fonction pour vectoriser la description avec Word2Vec
def vectorize_description_word2vec(description: str):
    tokens = preprocess_description(description)
    vectors = [word2vec_model.wv[word] for word in tokens if word in word2vec_model.wv]
    if vectors:
        word2vec_vector = np.mean(vectors, axis=0)
        word2vec_vector = normalize([word2vec_vector])[0].tolist()  # Normaliser le vecteur
        return word2vec_vector
    else:
        # Si aucun mot n'est dans le modèle, retourner un vecteur nul
        return np.zeros(word2vec_model.vector_size).tolist()

# Fonction pour vectoriser la description avec TF-IDF
def vectorize_description_tfidf(description: str):
    vector = vectorizer.transform([description])
    tfidf_vector = vector.toarray()[0].tolist()
    return tfidf_vector

# Fonction pour synchroniser les vecteurs dans les deux index TF-IDF et Word2Vec
def sync_tfidf_word2vec(document_id: str, description: str):
    # TF-IDF
    tfidf_vector = vectorize_description_tfidf(description)
    es.index(index="job_offers_tfidf", id=document_id, body={"description_vector": tfidf_vector})

    # Word2Vec
    word2vec_vector = vectorize_description_word2vec(description)
    es.index(index="job_offers_word2vec", id=document_id, body={"description_vector": word2vec_vector})

# Fonction pour vérifier les identifiants
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Fonction pour récupérer les informations d'un utilisateur depuis Elasticsearch
def get_user_from_db(username: str):
    try:
        response = es.get(index="identifiants", id=username)
        return response["_source"]
    except NotFoundError:
        return None

# Fonction d'authentification
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user_from_db(credentials.username)
    if user is None or not verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# Endpoint pour vérifier la santé de l'API (pas d'authentification)
@app.get("/")
def read_root():
    return {"status": "API is running"}

# Endpoint pour créer un document (nécessite authentification)
@app.post("/documents/add")
def create_document(document_id: str, payload: dict, user: dict = Depends(authenticate), response: Response = None):
    # Ajouter le document dans 'job_offers'
    es_response = es.index(index="job_offers", id=document_id, document=payload)

    # Synchroniser les vecteurs TF-IDF et Word2Vec
    description = payload.get("description", "")
    sync_tfidf_word2vec(document_id, description)
    response.headers["Cache-Control"] = "no-store"
    return {"result": es_response["result"]}

# Endpoint pour mettre à jour un document (nécessite authentification)
@app.put("/documents/update/{document_id}")
def update_document(document_id: str, payload: dict, user: dict = Depends(authenticate), response: Response = None):
    try:
        # Mettre à jour le document dans 'job_offers'
        es.get(index="job_offers", id=document_id)
        es_response = es.index(index="job_offers", id=document_id, document=payload)

        # Synchroniser les vecteurs TF-IDF et Word2Vec
        description = payload.get("description", "")
        sync_tfidf_word2vec(document_id, description)

        response.headers["Cache-Control"] = "no-store"
        return {"result": "updated"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

# Endpoint pour lire un document (nécessite authentification)
@app.get("/documents/{document_id}")
def read_document(document_id: str, user: dict = Depends(authenticate), response: Response = None):
    try:
        es_response = es.get(index="job_offers", id=document_id)
        
        response.headers["Cache-Control"] = "no-store"
        return es_response["_source"]
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

# Endpoint pour supprimer un document (nécessite authentification)
@app.delete("/documents/delete/{document_id}")
def delete_document(document_id: str, user: dict = Depends(authenticate), response: Response = None):
    try:
        # Supprimer le document des trois index
        es.delete(index="job_offers", id=document_id)
        es.delete(index="job_offers_tfidf", id=document_id)
        es.delete(index="job_offers_word2vec", id=document_id)
        
        response.headers["Cache-Control"] = "no-store"
        return {"result": "deleted"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")


@app.post("/documents/word2vec-similarity")
def get_word2vec_similar_documents(query: str, n: int = 5, user: dict = Depends(authenticate)):
    # Prétraiter et vectoriser la chaîne de caractères en utilisant Word2Vec
    query_tokens = preprocess_description(query)
    query_vector = [word2vec_model.wv[word] for word in query_tokens if word in word2vec_model.wv]
    
    if query_vector:
        query_vector = np.mean(query_vector, axis=0)  # Moyenne des vecteurs des mots pour obtenir un vecteur de phrase
    else:
        query_vector = np.zeros(word2vec_model.vector_size)  # Si aucun mot n'existe dans le modèle

    # Récupérer les vecteurs Word2Vec des documents depuis Elasticsearch
    search_body = {
        "size": 2500,  # Limite de la recherche
        "_source": ["description_vector"],
        "query": {
            "match_all": {}
        }
    }
    es_response = es.search(index="job_offers_word2vec", body=search_body, request_timeout=360)
    
    # Extraire les descriptions vectorisées et les identifiants des documents
    doc_vectors = []
    doc_ids = []
    for hit in es_response['hits']['hits']:
        doc_vectors.append(hit['_source']['description_vector'])
        doc_ids.append(hit['_id'])
    
    # Calculer la similarité cosinus entre la requête et chaque document
    doc_vectors = np.array(doc_vectors)
    query_vector = query_vector.reshape(1, -1)  # Redimensionner le vecteur de requête
    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    
    # Trouver les n documents les plus similaires
    most_similar_indices = similarities.argsort()[::-1][:n]
    most_similar_docs = [(doc_ids[i], similarities[i]) for i in most_similar_indices]
    
    return {"most_similar_documents": most_similar_docs}