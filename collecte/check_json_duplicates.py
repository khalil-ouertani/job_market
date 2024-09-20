import json

# Chemin vers le fichier JSON
json_file_path = 'data/franceTravail.json'

# Charger les données JSON depuis le fichier
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Fonction pour supprimer les doublons
def remove_duplicates(data):
    seen = []       # Liste pour stocker les éléments déjà vus
    unique_data = []  # Liste pour stocker les éléments uniques

    for item in data:
        if item not in seen:  # Si l'élément n'a pas été vu, on l'ajoute
            seen.append(item)
            unique_data.append(item)  # Ajouter à la liste des éléments uniques

    return unique_data

# Supprimer les doublons
clean_data = remove_duplicates(data)

# Afficher le nombre de doublons supprimés
num_removed = len(data) - len(clean_data)
if num_removed > 0:
    print(f"Nombre de doublons supprimés : {num_removed}")
else:
    print("Aucun doublon trouvé.")

# Réécrire le fichier JSON sans les doublons
with open(json_file_path, 'w', encoding='utf-8') as file:
    json.dump(clean_data, file, ensure_ascii=False, indent=4)

print("Fichier JSON mis à jour sans doublons.")
