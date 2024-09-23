import json
import time
from elasticsearch import Elasticsearch, helpers

es = None
retries = 10  # Nombre d'essais avant d'abandonner

for i in range(retries):
    try:
        es = Elasticsearch(['http://es-container:9200'])
        if es.ping():
            print("Connexion réussie à ElasticSearch")
            break
    except Exception as e:
        print(f"Essai {i+1}/{retries} : Connexion échouée, nouvelle tentative dans 20 secondes...")
        time.sleep(20)
else:
    raise ValueError("Impossible de se connecter à ElasticSearch après plusieurs essais")

def load_json_to_elasticsearch(json_file_path, index_name):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    actions = []
    for doc in data:
        actions.append({
            "_index": index_name,
            "_source": doc
        })

    helpers.bulk(es, actions)
    print(f"Chargement terminé pour l'index {index_name}")

# Charger le fichier Indeed dans ElasticSearch
load_json_to_elasticsearch('/app/indeed.json', 'data_jobs_raw_indeed') #insérer votre file_path

# Charger le fichier FranceTravail dans ElasticSearch
load_json_to_elasticsearch('/app/franceTravail.json', 'data_jobs_raw_francetravail') #insérer votre file_path
