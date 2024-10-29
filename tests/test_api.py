import requests

# L'URL de l'API déjà lancée dans un conteneur
API_URL = "http://localhost:8000"

# Test d'authentification correcte
def test_auth_success():
    response = requests.get(f"{API_URL}/documents/592a1d2ad89c3694954d3b802639c1a9", auth=('admin', 'admin'))
    assert response.status_code == 200

# Test d'authentification incorrecte
def test_auth_failure():
    response = requests.get(f"{API_URL}/documents/592a1d2ad89c3694954d3b802639c1a9", auth=('wrong_user', 'wrong_pass'))
    assert response.status_code == 401

# Test de création de document avec succès 
def test_create_document():
    payload = {"title": "Test Job", "description": "This is a test job"}
    response = requests.post(f"{API_URL}/documents/add?document_id=test1", json=payload, auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "created"}

# Test de lecture d'un document existant
def test_read_document():
    response = requests.get(f"{API_URL}/documents/test1", auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json()["title"] == "Test Job"

# Test de mise à jour de document
def test_update_document():
    updated_payload = {"title": "Updated Job", "description": "This is an updated test job"}
    response = requests.put(f"{API_URL}/documents/update/test1", json=updated_payload, auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "updated"}

# Test de suppression de document
def test_delete_document():
    response = requests.delete(f"{API_URL}/documents/delete/test1", auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "deleted"}
