import json
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

if not es.ping():
    raise ValueError("Connexion à ElasticSearch échouée")

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
load_json_to_elasticsearch('/home/ubuntu/job_market/data/indeed.json', 'data_jobs_raw_indeed') #insérer votre file_path

# Charger le fichier FranceTravail dans ElasticSearch
load_json_to_elasticsearch('/home/ubuntu/job_market/data/franceTravail.json', 'data_jobs_raw_francetravail') #insérer votre file_path
