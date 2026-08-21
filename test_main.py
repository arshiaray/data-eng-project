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
def test_get_recipes_default_limit():
    """Test fetching default list of recipes without specifying a category"""
    response = client.get("/recipes")
    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "recipes" in data
    assert isinstance(data["recipes"], list)

