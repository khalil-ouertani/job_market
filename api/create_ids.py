from elasticsearch import Elasticsearch
from passlib.context import CryptContext

# Connexion à Elasticsearch
es = Elasticsearch("http://localhost:9200")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def create_index_if_not_exists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"L'index '{index_name}' a été créé.")
    else:
        print(f"L'index '{index_name}' existe déjà.")

def create_user(username, password, index_name="identifiants"):
    create_index_if_not_exists(index_name)
    
    # Hacher le mot de passe et ajouter l'utilisateur dans l'index
    hashed_password = pwd_context.hash(password)
    user_data = {"username": username, "password": hashed_password}
    es.index(index=index_name, id=username, document=user_data)
    print(f"Utilisateur {username} créé avec succès dans l'index '{index_name}'.")

# Créer un utilisateur
create_user("admin", "admin")
create_user("khalil", "khalil_pass")