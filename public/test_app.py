import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from unittest.mock import patch, MagicMock
from app import app, mysql


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_secret_key"
    app.config["MYSQL_DB"] = "yolo"

    with app.app_context():
        with patch("app.mysql") as mock_mysql:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()

            mock_cursor.execute.return_value = None
            mock_cursor.fetchall.return_value = []  
            mock_cursor.fetchone.return_value = None

            mock_connection.cursor.return_value = mock_cursor
            mock_mysql.connection.return_value = mock_connection

            yield app.test_client()




def get_token(username, role):
    with app.test_request_context():
        token = create_access_token(identity={"username": username, "role": role})
    return token


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


@patch("app.execute_query")
def test_register(mock_execute_query, client):
    mock_execute_query.return_value = None
    response = client.post(
        "/api/auth/register",
        json={"username": "test_user", "password": "test_pass", "role": "user"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully."



@patch("app.fetch_data")  
def test_login_success(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {"username": "test_user", "password": "test_pass", "role": "user"}
    ]
    response = client.post(
        "/api/auth/login",
        json={"username": "test_user", "password": "test_pass"},
    )
    assert response.status_code == 200
    assert "token" in response.json


@patch("app.fetch_data")
def test_login_failure(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong_user", "password": "wrong_pass"},
    )
    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials."


def test_protected_endpoint(client):
    token = get_token("test_user", "user")
    response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json["message"] == "Token is valid!"


def test_protected_endpoint_invalid_token(client):
    response = client.get(
        "/api/test", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 422  


@patch("app.execute_query")
def test_role_restricted_endpoint(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/role_types",
        json={"description": "Admin role"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Role_type added successfully."


def test_role_restricted_endpoint_forbidden(client):
    token = get_token("test_user", "user")
    response = client.post(
        "/api/role_types",
        json={"description": "Should fail"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."



#ROLETYPES

@patch("app.fetch_data")
def test_get_role_types(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {"idrole_types": 1, "description": "Admin"},
        {"idrole_types": 2, "description": "User"}
    ]
    token = get_token("test_user", "user")
    response = client.get("/api/role_types", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["description"] == "Admin"


@patch("app.fetch_data")
def test_search_role_type(mock_fetch_data, client):
    mock_fetch_data.return_value = [{"idrole_types": 1, "description": "Admin"}]
    token = get_token("test_user", "user")
    response = client.get("/api/role_types/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json[0]["idrole_types"] == 1
    assert response.json[0]["description"] == "Admin"


@patch("app.fetch_data")
def test_search_role_type_not_found(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get("/api/role_types/99", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == []


@patch("app.execute_query")
def test_add_role_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/role_types",
        json={"description": "Manager"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Role_type added successfully."


@patch("app.execute_query")
def test_add_role_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.post(
        "/api/role_types",
        json={"description": "Manager"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_update_role_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/role_types/1",
        json={"description": "SuperAdmin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json["message"] == "Role_type updated successfully."


@patch("app.execute_query")
def test_update_role_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.put(
        "/api/role_types/1",
        json={"description": "SuperUser"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_role_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/role_types/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Role_type deleted successfully."


@patch("app.execute_query")
def test_delete_role_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.delete(
        "/api/role_types/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_role_type_not_found(mock_execute_query, client):
    mock_execute_query.return_value = 0  
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/role_types/99", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json["message"] == "Role_type not found."

#RELATIONSHIP_TYPES
@patch("app.fetch_data")
def test_get_relationship_types(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {"idrelationship_types": 1, "description": "Family"},
        {"idrelationship_types": 2, "description": "Friend"}
    ]
    token = get_token("test_user", "user")
    response = client.get("/api/relationship_types", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["description"] == "Family"


@patch("app.fetch_data")
def test_search_relationship_type(mock_fetch_data, client):
    mock_fetch_data.return_value = [{"idrelationship_types": 1, "description": "Family"}]
    token = get_token("test_user", "user")
    response = client.get("/api/relationship_types/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json[0]["idrelationship_types"] == 1
    assert response.json[0]["description"] == "Family"


@patch("app.fetch_data")
def test_search_relationship_type_not_found(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get("/api/relationship_types/99", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == []


@patch("app.execute_query")
def test_add_relationship_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/relationship_types",
        json={"description": "Colleague"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Relationship_type added successfully."


@patch("app.execute_query")
def test_add_relationship_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.post(
        "/api/relationship_types",
        json={"description": "Colleague"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_update_relationship_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/relationship_types/1",
        json={"description": "Work Colleague"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json["message"] == "Relationship_type updated successfully."


@patch("app.execute_query")
def test_update_relationship_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.put(
        "/api/relationship_types/1",
        json={"description": "Acquaintance"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_relationship_type(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/relationship_types/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Relationship_type deleted successfully."


@patch("app.execute_query")
def test_delete_relationship_type_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.delete(
        "/api/relationship_types/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_relationship_type_not_found(mock_execute_query, client):
    mock_execute_query.return_value = 0  
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/relationship_types/99", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json["message"] == "Relationship_type not found."
    
    
# DONATIONS
@patch("app.execute_query")
def test_add_donation(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/donations",
        json={
            "individual_id": 2,
            "date": "2023-12-01",
            "ampoule_count": 5,
            "motilitiy_rating": 4.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Donation added successfully."

def test_add_donation_missing_fields(client):
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/donations",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert (
        response.status_code == 400
    )  


@patch("app.fetch_data")
def test_get_donations(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {
            "iddonations": 1,
            "individual_id": 2,
            "date": "2023-12-01",
            "ampoule_count": 5,
            "motilitiy_rating": 4.5,
        }
    ]
    token = get_token("test_user", "user")
    response = client.get("/api/donations", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["iddonations"] == 1


@patch("app.fetch_data")
def test_search_donations(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {
            "iddonations": 1,
            "individual_id": 2,
            "date": "2023-12-01",
            "ampoule_count": 5,
            "motilitiy_rating": 4.5,
        }
    ]
    token = get_token("test_user", "user")
    response = client.get(
        "/api/donations/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json[0]["iddonations"] == 1


@patch("app.fetch_data")
def test_search_donations_not_found(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get(
        "/api/donations/99", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json == []


@patch("app.execute_query")
def test_update_donation(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/donations/1",
        json={
            "individual_id": 3,
            "date": "2023-12-02",
            "ampoule_count": 6,
            "motilitiy_rating": 4.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json["message"] == "Donation updated successfully."


@patch("app.execute_query")
def test_update_donation_missing_fields(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/donations/1",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


@patch("app.execute_query")
def test_delete_donation(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/donations/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Donation deleted successfully."


@patch("app.execute_query")
def test_delete_donation_not_found(mock_execute_query, client):
    mock_execute_query.return_value = 0  
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/donations/99", headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json)

    assert response.status_code == 404
    assert response.json["message"] == "Donation not found."



@patch("app.fetch_data")
def test_get_donations_empty(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get("/api/donations", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == []


#INDIVIDUALS
@patch("app.fetch_data")
def test_get_individuals(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {"idindividuals": 1, "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"},
        {"idindividuals": 2, "first_name": "Jane", "last_name": "Smith", "email": "jane.smith@example.com"}
    ]
    token = get_token("test_user", "user")
    response = client.get("/api/individuals", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["first_name"] == "John"


@patch("app.fetch_data")
def test_search_individual(mock_fetch_data, client):
    mock_fetch_data.return_value = [{"idindividuals": 1, "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}]
    token = get_token("test_user", "user")
    response = client.get("/api/individuals/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json[0]["idindividuals"] == 1
    assert response.json[0]["first_name"] == "John"


@patch("app.fetch_data")
def test_search_individual_not_found(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get("/api/individuals/99", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == []

@patch("app.execute_query")
def test_add_individual(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/individuals",
        json={
            "type_id": 1,
            "birthdate": "1990-01-01",
            "is_male": True,
            "fname": "John",
            "mname": "Doe",
            "lname": "Smith",
            "address": "123 Main St",
            "contact": "123-456-7890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json["message"] == "Individual added successfully."


@patch("app.execute_query")
def test_add_individual_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.post(
        "/api/individuals",
        json={"first_name": "Alice", "last_name": "Brown", "email": "alice.brown@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_update_individual(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/individuals/1",
        json={
            "type_id": 1,
            "birthdate": "1990-01-01",
            "is_male": True,
            "fname": "John",
            "mname": "Doe",
            "lname": "Smith",
            "address": "123 Main St",
            "contact": "123-456-7890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Individual updated successfully."


@patch("app.execute_query")
def test_update_individual_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.put(
        "/api/individuals/1",
        json={"first_name": "John", "last_name": "Doe", "email": "john.doe_updated@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_individual(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/individuals/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Individual deleted successfully."


@patch("app.execute_query")
def test_delete_individual_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.delete(
        "/api/individuals/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_individual_not_found(mock_execute_query, client):
    mock_execute_query.return_value = 0  
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/individuals/99", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json["message"] == "Individual not found."
    
    
#RELATIONSHIPS

@patch("app.fetch_data")
def test_get_relationships(mock_fetch_data, client):
    mock_fetch_data.return_value = [
        {"idrelationships": 1, "individual_id_1": 1, "individual_id_2": 2, "relationship_type_id": 1},
        {"idrelationships": 2, "individual_id_1": 3, "individual_id_2": 4, "relationship_type_id": 2}
    ]
    token = get_token("test_user", "user")
    response = client.get("/api/relationships", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["individual_id_1"] == 1


@patch("app.fetch_data")
def test_search_relationship(mock_fetch_data, client):
    mock_fetch_data.return_value = [{"idrelationships": 1, "individual_id_1": 1, "individual_id_2": 2, "relationship_type_id": 1}]
    token = get_token("test_user", "user")
    response = client.get("/api/relationships/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json[0]["idrelationships"] == 1
    assert response.json[0]["individual_id_1"] == 1


@patch("app.fetch_data")
def test_search_relationship_not_found(mock_fetch_data, client):
    mock_fetch_data.return_value = []
    token = get_token("test_user", "user")
    response = client.get("/api/relationships/99", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == []


@patch("app.execute_query")
def test_add_relationship(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.post(
        "/api/relationships",
        json={
            "type_id": 1,
            "individual_1_id": 1,
            "individual_2_id": 2,
            "date_start": "2023-01-01",
            "date_end": "2023-12-31"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json["message"] == "Relationship added successfully."


@patch("app.execute_query")
def test_add_relationship_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.post(
        "/api/relationships",
        json={"individual_id_1": 1, "individual_id_2": 2, "relationship_type_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_update_relationship(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.put(
        "/api/relationships/1",
        json={
            "type_id": 2,
            "individual_1_id": 1,
            "individual_2_id": 3,
            "date_start": "2023-01-01",
            "date_end": "2023-12-31"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Relationship updated successfully."


@patch("app.execute_query")
def test_update_relationship_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.put(
        "/api/relationships/1",
        json={"individual_id_1": 1, "individual_id_2": 3, "relationship_type_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_relationship(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/relationships/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Relationship deleted successfully."


@patch("app.execute_query")
def test_delete_relationship_forbidden(mock_execute_query, client):
    mock_execute_query.return_value = None
    token = get_token("test_user", "user")
    response = client.delete(
        "/api/relationships/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Access forbidden."


@patch("app.execute_query")
def test_delete_relationship_not_found(mock_execute_query, client):
    mock_execute_query.return_value = 0  
    token = get_token("admin_user", "admin")
    response = client.delete(
        "/api/relationships/99", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json["message"] == "Relationship not found."