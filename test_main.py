from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

#initialise TestClient with the FastAPI app
client = TestClient(app)

#test 1: check endpoint connection
def test_read_root():
  response = client.get("/")
  assert response.status_code == 200
  assert response.json() == {"message": "Recipe API is live and connected to PostgreSQL!"}

#test 2: basic recipe fetch
@patch("main.get_db_connection")
def test_get_recipes_default_limit(mock_db):
    """Test fetching default list of recipes without specifying a category"""
    # Create simple fake cursor and connection
    fake_conn = MagicMock()
    fake_cursor = MagicMock()

    # Set fake return values for database calls
    fake_cursor.fetchone.return_value = (1,)
    fake_cursor.fetchall.return_value = [
        ("123", "Teriyaki Chicken", "Chicken", "Japanese")
    ]

    # Wire them up
    fake_conn.cursor.return_value = fake_cursor
    mock_db.return_value = fake_conn

    # Run test
    response = client.get("/recipes")
    assert response.status_code == 200

#test 3: filtering by category
@patch("main.get_db_connection")
def test_get_recipes_with_category_filter(mock_db):
    """Test filtering recipes by category."""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()

    fake_cursor.fetchone.return_value = (1,)
    fake_cursor.fetchall.return_value = [
        ("456", "Grilled Salmon", "Seafood", "Seafood")
    ]

    fake_conn.cursor.return_value = fake_cursor
    mock_db.return_value = fake_conn

    response = client.get("/recipes?category=Seafood&limit=5")
    assert response.status_code == 200

#test 4: error handling for non existent recipe
@patch("main.get_db_connection")
def test_get_recipe_by_id_not_found(mock_db):
    """Test fetching a recipe by an ID that does not exist."""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()

    # Simulate no record found in DB
    fake_cursor.fetchone.return_value = None

    fake_conn.cursor.return_value = fake_cursor
    mock_db.return_value = fake_conn

    response = client.get("/recipes/999999")
    assert response.status_code == 404