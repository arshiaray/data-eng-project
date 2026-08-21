from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

#initialise TestClient with the FastAPI app
client = TestClient(app)

#test 1: check endpoint connection
def test_read_root():
    """Test the root endpoint to ensure the API is live and connected to PostgreSQL."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Recipe API is live and connected to PostgreSQL!"}

#test 2: basic recipe fetch
@patch("main.get_db_connection")
def test_get_recipes_default_limit(mock_get_db_connection):
    """Test fetching default list of recipes without specifying a category"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    #simulate DB returning a count of 1 and 1 recipe row
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.fetchall.return_value = [("123", "Teriyaki Chicken", "Chicken", "Japanse")]

    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    response = client.get("/recipes")
    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "recipes" in data
    assert isinstance(data["recipes"], list)
    assert data["count"] == 1

#test 3: filtering by category
@patch("main.get_db_connection")
def test_get_recipes_with_category_filter(mock_get_db_connection):
    """Test filtering recipes by category."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    #simulate DB returning a count of 1 and a seafood recipe row
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.fetchall.return_value = [("456", "Grilled Salmon", "Seafood")]

    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    response = client.get("/recipes?category=Seafood&limit=5")
    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "recipes" in data
    assert data["count"] <= 5
    for recipe in data["recipes"]:
        assert recipe["category"].lower() == "seafood"

#test 4: error handling for non existent recipe
@patch("main.get_db_connection")
def test_get_recipe_by_id_not_found(mock_get_db_connection):
    """Test fetching a recipe by an ID that does not exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    #simulate fetchone returning no record found
    mock_cursor.fetchone.return_value = None

    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn
    
    response = client.get("/recipes/999999")  # assuming this ID does not exist
    assert response.status_code == 404
    assert response.json() == {"detail": "Recipe not found"}