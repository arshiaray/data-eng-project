from fastapi.testclient import TestClient
from main import app

#initialise TestClient with the FastAPI app
client = TestClient(app)

