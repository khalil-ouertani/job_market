import json
import time
import hashlib
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

def generate_unique_id(job_offer):
    job_str = json.dumps(job_offer, sort_keys=True).encode('utf-8')
    return hashlib.md5(job_str).hexdigest()

def load_data_to_elasticsearch(index_name, data):
    for job in data:
        # Générer un identifiant unique pour chaque offre de travail
        job_id = generate_unique_id(job)
        
        # Charger les données dans ElasticSearch avec un ID unique
        es.index(index=index_name, id=job_id, body=job)

# Charger les fichiers JSON
with open('/app/indeed.json', 'r', encoding='utf-8') as indeed_file:
    indeed_data = json.load(indeed_file)

with open('/app/franceTravail.json', 'r', encoding='utf-8') as france_travail_file:
    france_travail_data = json.load(france_travail_file)

# Fusionner les deux ensembles de données
all_jobs = indeed_data + france_travail_data

# Créer un index si ce n'est pas déjà fait
index_name = 'job_offers'
if es.indices.exists(index=index_name):
    es.indices.delete(index=index)
    print(f"Indice {index_name} supprimé avec succès.")
    es.indices.create(index=index_name)
    print(f"Indice {index_name} recréé avec succès.")
else:
    es.indices.create(index=index_name)
    print(f"Indice {index_name} créé avec succès.")

# Charger les données dans ElasticSearch
load_data_to_elasticsearch(index_name, all_jobs)

with open("/data/chargement_done.txt", "w") as f:
    f.write("chargement completed")

print("Fichier de signalisation créé avec succès")

print(f"{len(all_jobs)} offres de travail chargées dans l'index {index_name} avec succès.")
