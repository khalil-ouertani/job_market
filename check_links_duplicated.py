# Chemin vers le fichier texte contenant les liens
file_path = 'job_links.txt'

def count_duplicates(file_path):
    try:
        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as file:
            links = file.readlines()

        # Nettoyer les liens (enlever les espaces et sauts de ligne)
        cleaned_links = [link.strip() for link in links]

        # Utiliser un dictionnaire pour compter les occurrences de chaque lien
        link_counts = {}
        for link in cleaned_links:
            if link in link_counts:
                link_counts[link] += 1
            else:
                link_counts[link] = 1

        # Filtrer les liens qui apparaissent plus d'une fois (doublons)
        duplicates = {link: count for link, count in link_counts.items() if count > 1}

        # Afficher les résultats
        if duplicates:
            print(f"Nombre total de doublons : {sum(duplicates.values()) - len(duplicates)}")
            for link, count in duplicates.items():
                print(f"Le lien '{link}' apparaît {count} fois.")
        else:
            print("Aucun doublon détecté.")

    except FileNotFoundError:
        print(f"Le fichier {file_path} n'existe pas.")

# Appeler la fonction pour compter les doublons
count_duplicates(file_path)
