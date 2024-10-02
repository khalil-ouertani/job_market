import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

client = TestClient(app)

# Test d'authentification correcte
def test_auth_success():
    response = client.get("/documents/592a1d2ad89c3694954d3b802639c1a9", auth=('admin', 'admin'))
    assert response.status_code == 200

# Test d'authentification incorrecte
def test_auth_failure():
    response = client.get("/documents/592a1d2ad89c3694954d3b802639c1a9", auth=('wrong_user', 'wrong_pass'))
    assert response.status_code == 401

# Test de création de document avec succès
def test_create_document():
    payload = {"title": "Test Job", "description": "This is a test job"}
    response = client.post("/documents/add?document_id=test1", json=payload, auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "created"}

# Test de lecture d'un document existant
def test_read_document():
    response = client.get("/documents/test1", auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json()["title"] == "Test Job"

# Test de mise à jour de document
def test_update_document():
    updated_payload = {"title": "Updated Job", "description": "This is an updated test job"}
    response = client.put("/documents/update/test1", json=updated_payload, auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "updated"}

# Test de suppression de document
def test_delete_document():
    response = client.delete("/documents/delete/test1", auth=('admin', 'admin'))
    assert response.status_code == 200
    assert response.json() == {"result": "deleted"}
