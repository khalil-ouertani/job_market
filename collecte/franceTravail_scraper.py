import requests
import json
import pandas as pd


def authenticate():

    url = 'https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}    

    params = {
        'grant_type': 'client_credentials',
        'scope': 'api_offresdemploiv2 o2dsoffre'
    }

    params['client_id'] = FRANCETRAVAIL_ID_CLIENT
    params['client_secret'] = FRANCETRAVAIL_CLE_SECRETE

    response = requests.post(url=url,data=params,headers=headers)
    response = json.loads(response.text)
    return response['access_token']

# Fonction pour récupérer tout le contenu en plusieurs requêtes
def fetch_all_content(url, headers):
    all_content = []
    byte_start = 0     
    total_size = None 
    chunk_size = 150   # Taille des portions

    while True:
        
        byte_end = byte_start + chunk_size - 1
        
        response = requests.get(url+f'{byte_start}-{byte_end}', headers=headers)

        if response.status_code == 206:
            all_content.append(response.json()['resultats'])

            content_range = response.headers['Content-Range']
            print(f"Récupéré: {content_range}")

            # Extraire la taille totale si elle n'a pas encore été définie
            if total_size is None:
                total_size = int(content_range.split('/')[1])

            byte_start += chunk_size  # Passer à la portion suivante

            if byte_start >= total_size:
                break
        else:
            print(f"Erreur: Code de réponse {response.status_code}")
            break

    return all_content

if __name__ == "__main__":
    FRANCETRAVAIL_HOST = 'https://api.francetravail.io'
    FRANCETRAVAIL_ID_CLIENT = 'PAR_jobmarket_60bad4aa0142d8ca1dd59e5dacdf039d0887bed06e19be28370d798f188a3928'
    FRANCETRAVAIL_CLE_SECRETE = '39c354f5fa2bd7c28f26944e948ddd24d4d30708a1f9e7650df341721368513f'

    SEARCH_URL = f"{FRANCETRAVAIL_HOST}/partenaire/offresdemploi/v2/offres/search?motsCles=data&range="

    access_token = authenticate()
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }
    
    all_content = fetch_all_content(SEARCH_URL, headers)
    all_content = pd.Series(all_content).explode().tolist()
    
    # Exporter en fichier JSON
    with open("data/franceTravail.json", "w", encoding="utf-8") as fichier:
        json.dump(all_content, fichier, ensure_ascii=False, indent=4)