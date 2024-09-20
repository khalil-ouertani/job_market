from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Fonction pour créer un User-Agent aléatoire
def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    ]
    return random.choice(user_agents)

def create_driver():
    options = Options()
    
    # Ajouter un User-Agent aléatoire
    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")
        
    # Créer une instance de driver avec les options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(), port=9515), options=options)
    return driver

def load_existing_links(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()  # Si le fichier n'existe pas, retourner un ensemble vide

def scrape_job_links(driver, url, existing_links):
    driver.get(url)
    time.sleep(random.uniform(3, 10))  # Attendre un délai aléatoire

    job_links = []
    
    # Extraire les offres d'emploi sur la page
    jobs = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')
    
    for job in jobs:
        try:
            link = job.find_element(By.TAG_NAME, "a").get_attribute('href')

            # Vérifier si le lien est déjà dans la liste des liens existants
            if link and link not in existing_links:
                job_links.append(link)
                existing_links.add(link)  # Ajouter le nouveau lien aux liens existants
        except Exception as e:
            print(f"Erreur lors de l'extraction d'une offre : {e}")
    
    return job_links

def scrape_job_links_multiple_pages(driver, start_url, num_pages, existing_links):
    base_url = start_url
    all_job_links = []
    
    for i in range(num_pages):
        print(f"Scraping la page {i+1}")
        
        try:
            # Scraper la page et vérifier les doublons
            job_links = scrape_job_links(driver, start_url, existing_links)
            all_job_links.extend(job_links)
        except Exception as e:
            print(f"Erreur lors du scraping de la page {i+1} : {e}")
        
        # Attendre un délai aléatoire avant de passer à la page suivante
        time.sleep(random.uniform(10, 20))
        
        # Construire l'URL pour la page suivante (ajuster la logique en fonction du site)
        start_url = base_url + f"&start={(i+1) * 10}"  # Incrementation pour la pagination
    
    return all_job_links

#cities = ['Île-de-France','Marseille','Lyon','Toulouse','Lille', 'Nantes', 'Nice','Strasbourg', 'Montpellier', 'Bordeaux', 'Rennes']
cities = ['Strasbourg', 'Montpellier', 'Bordeaux', 'Rennes']
if __name__ == "__main__":
    
    driver = create_driver()
    for city in cities:
        base_url = f"https://fr.indeed.com/jobs?q=data&l={city}&from=searchOnHP"
        num_pages = 15
        file_path = "job_links.txt"
        toscrap_file_path = "job_links_toscrap.txt"

        # Charger les liens existants depuis le fichier
        existing_links = load_existing_links(file_path)

        # Scraper les nouvelles offres
        new_job_links = scrape_job_links_multiple_pages(driver, base_url, num_pages, existing_links)

        # Sauvegarder les nouveaux liens dans le fichier sans duplicata
        with open(file_path, "a", encoding="utf-8") as fichier:
            for link in new_job_links:
                fichier.write(f"{link}\n")
                
        with open(toscrap_file_path, "a", encoding="utf-8") as fichier:
            for link in new_job_links:
                fichier.write(f"{link}\n")
        
        print(f"---------------- Scraping DONE for {city} ! ----------------")
        
    driver.quit()