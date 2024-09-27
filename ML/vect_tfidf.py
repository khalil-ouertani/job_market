from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

index_name = 'job_offers'

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

descriptions = [job['description'] if job['description'] is not None else '' for job in job_offers]

# Calculer les vecteurs TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(descriptions)

tfidf_documents = []
for idx, job_offer in enumerate(job_offers):
    tfidf_vector = tfidf_matrix[idx].toarray().tolist()[0]  # Convertir le vecteur sparse en une liste
    tfidf_documents.append({
        "id": job_offer['id'],
        "description_vector": tfidf_vector
    })

index_tfidf = 'job_offers_tfidf'

# Vérifier si le nouvel index existe, sinon le créer
if not es.indices.exists(index=index_tfidf):
    es.indices.create(index=index_tfidf)

# Charger les documents avec vecteurs TF-IDF dans Elasticsearch
for doc in tfidf_documents:
    es.index(index=index_tfidf, id=doc["id"], body={"description_vector": doc["description_vector"]})

print(f"Chargement des vecteurs TF-IDF dans l'index '{index_tfidf}' terminé.")