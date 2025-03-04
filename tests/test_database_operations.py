"""
test_database_routes.py
This test suite validates the functionality of the FastAPI-based database routes.

Covered Tests:
1.  Ensures the test database is properly initialized.
2.  Verifies table creation, data insertion, and edge cases.
3. FastAPI Endpoints:
   - `/log_api_call`: Tests logging API calls with valid and invalid data.
   - `/get_api_call`: Checks retrieval of logged API calls.
4. Error Handling:
   - Missing fields in requests.
   - Large payload handling.
   - Cleanup of the temporary database after test execution.

Mocking:
- Uses `pytest` fixtures for database setup.
- Employs `TestClient` to simulate API requests.

"""
import pytest
import sqlite3
import os
import tempfile
from fastapi.testclient import TestClient
from database.db import DB
from database.table_methods import TableMethods
import database.routes
from database.routes import app

# Create a temporary file for our test database
temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db').name

def get_test_db():
    """Return a DB instance using our temporary file."""
    return DB(sqlite3, temp_db_file)

database.routes.get_db = get_test_db # Monkeypatch the get_db function in routes.py
client = TestClient(app) # Use TestClient to test FastAPI routes


@pytest.fixture
def test_db():
    """
    Pytest fixture to work with the test database.
    """
    db = get_test_db()
    table_methods = TableMethods(db)
    
    # Create the API_calls table if it doesn't exist
    columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "params": "TEXT",
        "url": "TEXT NOT NULL",
        "response": "TEXT NOT NULL",
        "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    }
    table_methods.create_table("API_calls", columns)
    
    # Clear any existing data
    db.execute("DELETE FROM API_calls")
    db.commit()
    
    yield table_methods
    db.close()


def test_create_table(test_db):
    """
    Test if the table is created successfully.
    """
    db = test_db.db
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='API_calls';")
    assert cursor.fetchone() is not None, "Table 'API_calls' does not exist."


def test_insert_to_table(test_db):
    """
    Test inserting valid data into the table.
    """
    data_to_insert = {
        "params": '{"key": "value"}',
        "url": "https://example.com",
        "response": "Success"
    }
    test_db.insert_to_table("API_calls", data_to_insert)

    cursor = test_db.db.execute("SELECT * FROM API_calls WHERE url = ? AND params = ?", ("https://example.com", '{"key": "value"}'))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == '{"key": "value"}'
    assert result[2] == "https://example.com"
    assert result[3] == "Success"


def test_insert_empty_data(test_db):
    """
    Test inserting empty data into the table (edge case).
    """
    with pytest.raises(Exception, match="Error inserting data"):
        test_db.insert_to_table("API_calls", {})  # No data provided


def test_log_api_call_endpoint():
    """
    Test the /log_api_call endpoint of the FastAPI application with valid data.
    """
    data = {
        "params": {"key": "value"},
        "url": "https://api.example.com",
        "response": "OK"
    }

    response = client.post("/log_api_call", json=data)

    assert response.status_code == 200
    response_data = response.json()["data"]
    assert response_data["url"] == "https://api.example.com"
    assert response_data["response"] == "OK"
    assert "timestamp" in response_data


def test_log_api_call_missing_fields():
    """
    Test sending incomplete data to the /log_api_call endpoint.
    """
    incomplete_event_data = {
        "params": {"key": "value"}
    }

    response = client.post("/log_api_call", json=incomplete_event_data)
    assert response.status_code == 422


def test_log_api_call_empty_fields():
    """
    Test sending empty URL to the /log_api_call endpoint.
    """
    event_data = {
        "params": {"key": "value"},
        "url": "",
        "response": "OK"
    }

    response = client.post("/log_api_call", json=event_data)
    assert response.status_code == 400

def test_get_api_call_endpoint(test_db):
    """
    Test the /get_api_call endpoint for fetching stored API calls.
    """
    data = {
        "params": {"key": "value"},
        "url": "https://api.example.com",
        "response": "OK"
    }

    post_response = client.post("/log_api_call", json=data)
    assert post_response.status_code == 200
    assert "data" in post_response.json()
    assert post_response.json()["data"]["url"] == "https://api.example.com"
    request_data = {
        "params": {"key": "value"},
        "url": "https://api.example.com"
    }

    response = client.post("/get_api_call", json=request_data)
    assert response.status_code == 200
    response_data = response.json()["data"]
    assert response_data is not None 
    assert len(response_data) > 0
    assert response_data[0]["url"] == "https://api.example.com"

def test_process_event_large_payload():
    """
    Test sending a large payload to the /log_api_call endpoint.
    """
    large_data = {
        "params": {"key": "value"},
        "url": "https://api.example.com",
        "response": "OK" * 1000000  # Large response
    }

    response = client.post("/log_api_call", json=large_data)
    assert response.status_code == 200


def pytest_sessionfinish(session, exitstatus):
    """
    Remove the temporary database file after all tests have completed.
    this funcrion has a special function name that pytest recognizes.
    When pytest finishes executing all tests, it looks for functions with this specific name.
    """
    try:
        os.unlink(temp_db_file) # Remove the temporary database file
    except OSError as e:
        print(f"Error cleaning up temporary file: {e}")