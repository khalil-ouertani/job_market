import json
import pandas as pd
import numpy as np
import re
from elasticsearch import Elasticsearch, helpers


def normalize_data(france_travail_file, indeed_file):
    normalized_data = []

    # Charger et normaliser les données de FranceTravail
    with open(france_travail_file, 'r') as ft_file:
        france_data = json.load(ft_file)
        for offer in france_data:
            normalized_data.append({
                "type_contrat": offer.get("typeContrat"),
                "region": offer.get("lieuTravail", {}).get("libelle"),
                "secteur": offer.get("secteurActiviteLibelle")
            })

    # Charger et normaliser les données d'Indeed
    with open(indeed_file, 'r') as in_file:
        indeed_data = json.load(in_file)
        for offer in indeed_data:
            normalized_data.append({
                "type_contrat": offer.get("contract_type"),
                "region": offer.get("job_location"),
                "secteur": offer.get("company_industry")
            })

    return normalized_data  # Retourne directement les données au lieu de les sauvegarder

# Appeler la fonction et charger les données dans 'data'
data = normalize_data('data/franceTravail.json', 'data/indeed.json')

# Convertir en DataFrame
df = pd.DataFrame(data)

# Normalisation des secteurs
secteur_categories = {
    'Informatique': 'Informatique et Télécommunications',
    'Télécommunications': 'Informatique et Télécommunications',
    'Internet': 'Informatique et Télécommunications',
    'Programmation': 'Informatique et Télécommunications',
    'Traitement de données': 'Informatique et Télécommunications',
    
    'Conseil': 'Conseil et Services aux Entreprises',
    'Gestion': 'Conseil et Services aux Entreprises',
    'Études techniques': 'Conseil et Services aux Entreprises',
    'Support aux entreprises': 'Conseil et Services aux Entreprises',
    
    'Santé': 'Santé et Services Sociaux',
    'Médecin': 'Santé et Services Sociaux',
    'Hôpital': 'Santé et Services Sociaux',
    'Action sociale': 'Santé et Services Sociaux',
    
    'Assurance': 'Finance et Assurance',
    'Banque': 'Finance et Assurance',
    'Finance': 'Finance et Assurance',
    'Holding': 'Finance et Assurance',
    'Crédit': 'Finance et Assurance',
    
    'Commerce': 'Commerce et Distribution',
    'Vente': 'Commerce et Distribution',
    'Distribution': 'Commerce et Distribution',
    'Retail': 'Commerce et Distribution',

    'Agriculture': 'Agriculture et Alimentation',
    'Alimentation': 'Agriculture et Alimentation',
    'Vin': 'Agriculture et Alimentation',
    
    'Énergie': 'Énergie et Environnement',
    'Combustible': 'Énergie et Environnement',
    'Gaz': 'Énergie et Environnement',
    'Électricité': 'Énergie et Environnement',
    
    'Transport': 'Transport et Logistique',
    'Logistique': 'Transport et Logistique',
    'Livraison': 'Transport et Logistique',
    'Ferroviaire': 'Transport et Logistique',
    'Routier': 'Transport et Logistique',
    
    'Industrie': 'Industrie Manufacturière',
    'Production': 'Industrie Manufacturière',
    'Manufacture': 'Industrie Manufacturière',
    'Fabrication': 'Industrie Manufacturière',
    'Matériel': 'Industrie Manufacturière',
    
    'Recherche': 'Recherche et Développement',
    'Développement': 'Recherche et Développement',
    'Biotechnologie': 'Recherche et Développement',
    
    'Enseignement': 'Éducation et Formation',
    'Formation': 'Éducation et Formation',
    'Éducation': 'Éducation et Formation',
    
    'Publicité': 'Marketing et Communication',
    'Marketing': 'Marketing et Communication',
    'Relations publiques': 'Marketing et Communication',
    
    'Sécurité': 'Sécurité et Défense',
    'Défense': 'Sécurité et Défense',
    
    'Immobilier': 'Immobilier',
    'Hôtellerie': 'Hôtellerie et Tourisme',
    'Tourisme': 'Hôtellerie et Tourisme',
    
    'Organisation': 'Organismes Non Gouvernementaux et Associations',
    'ONG': 'Organismes Non Gouvernementaux et Associations',
    'Associations': 'Organismes Non Gouvernementaux et Associations',
    
    'Architect': 'Architecture et Ingénierie',
    'Ingénierie': 'Architecture et Ingénierie',
    
    'Justice': 'Services Juridiques',
    'Juridique': 'Services Juridiques',
    
    'Culture': 'Arts, Culture et Divertissement',
    'Divertissement': 'Arts, Culture et Divertissement',
    'Loisirs': 'Arts, Culture et Divertissement',
    'Médias': 'Arts, Culture et Divertissement',
}

# Fonction de normalisation des secteurs
def normaliser_secteur(sector):
    if pd.isna(sector):
        return 'Autre'
    for keyword, category in secteur_categories.items():
        if keyword.lower() in sector.lower():
            return category
    return 'Autre'  # Cas par défaut pour les secteurs non identifiés

# Application de la fonction de normalisation
df['secteur_normalisé'] = df['secteur'].apply(normaliser_secteur)

# Normalisation des types de contrat
df['type_contrat'] = df['type_contrat'].replace({
    'MIS': 'Intérim',
    'CDI': 'CDI',
    'cdi': 'CDI',
    'CDD': 'CDD',
    'cdd': 'CDD',
    None: 'None'  # Remplace les valeurs nulles par 'None'
})

# Fonction de nettoyage et de normalisation des régions
def nettoyer_region(region):
    if pd.isna(region):
        return 'None'
    
    # Supprimer les codes postaux et conserver uniquement le nom de la ville/région
    match = re.match(r'^\d+\s*-\s*(.*)', region)
    if match:
        ville = match.group(1)
    else:
        ville = region
    
    # Capitaliser chaque mot pour homogénéiser
    ville = ville.title()
    
    # Normalisation des noms de grandes villes multi-arrondissements
    if re.match(r'Paris \d+|Paris \d+E Arrondissement', ville, re.IGNORECASE):
        return 'Paris'
    elif re.match(r'Lyon \d+|Lyon \d+E Arrondissement', ville, re.IGNORECASE):
        return 'Lyon'
    elif re.match(r'Marseille \d+|Marseille \d+E Arrondissement', ville, re.IGNORECASE):
        return 'Marseille'
    
    # Normalisation des noms de régions spécifiques
    ville = ville.replace('Ile-De-France', 'Île-de-France')
    ville = ville.replace('Loire Atlantique', 'Loire-Atlantique')
    ville = ville.replace('Hauts De Seine', 'Hauts-de-Seine')
    ville = ville.replace('Seine Saint Denis', 'Seine-Saint-Denis')
    ville = ville.replace('Val De Marne', 'Val-de-Marne')
    ville = ville.replace('Puy De Dôme', 'Puy-de-Dôme')
    ville = ville.replace('Rhin (Bas)', 'Bas-Rhin')
    ville = ville.replace('Garonne (Haute)', 'Haute-Garonne')
    ville = ville.replace('Savoie (Haute)', 'Haute-Savoie')
    ville = ville.replace('Bouches Du Rhône', 'Bouches-du-Rhône')
    ville = ville.replace("Provence-Alpes-Cote D'Azur", 'Provence-Alpes-Côte d\'Azur')
    
    # Enlever les éventuels codes restants seuls
    if re.match(r'^\d+$', ville):
        return 'None'  # Remplace par 'None' si le champ contient seulement un code
    
    return ville

# Application de la fonction à chaque élément de la colonne 'region'
df['region_normalisee'] = df['region'].apply(nettoyer_region)

# Supprimer les colonnes non normalisées
df = df.drop(columns=['region', 'secteur'])

es = Elasticsearch(['http://localhost:9200'])

def load_data_to_elasticsearch(index_name, data):
    # Convertir le DataFrame en dictionnaire JSON
    records = data.to_dict(orient='records')
    
    # Préparer les actions pour bulk API
    actions = [
        {
            "_index": index_name,
            "_source": record
        }
        for record in records
    ]
    
    # Charger les données dans Elasticsearch
    helpers.bulk(es, actions)
    print(f"Les données ont été chargées avec succès dans l'index {index_name}.")

load_data_to_elasticsearch('job_offers_viz', df)