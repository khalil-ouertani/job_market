import os
import subprocess
import time

# Chemin vers le fichier texte et le fichier Python
txt_file_path = 'job_links_toscrap.txt'
python_file_path = 'extern_indeed_job_scraper.py'

def is_file_empty(file_path):
    """Vérifie si le fichier texte est vide."""
    try:
        with open(file_path, 'r') as file:
            # Lire le contenu du fichier
            content = file.read().strip()
            # Si le contenu est vide, le fichier est considéré comme vide
            return len(content) == 0
    except FileNotFoundError:
        print(f"Le fichier {file_path} n'existe pas.")
        return True

def run_python_file(file_path):
    """Exécute le fichier Python."""
    try:
        subprocess.run(['python', file_path], check=True)
        print(f"{file_path} exécuté avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de {file_path}: {e}")

# Boucle principale
while not is_file_empty(txt_file_path):
    # Exécuter le script Python
    run_python_file(python_file_path)
    
    # Attendre un certain temps avant de vérifier à nouveau (par exemple 5 secondes)
    time.sleep(5)

print("Le fichier texte est vide. Arrêt du script.")