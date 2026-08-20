import os
import psycopg2
import requests
import json

#db connection credentials from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "meal_db")
DB_USER = os.getenv("DB_USER", "my_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "my_password")

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


def initialise_db():
    """Creates the meals table in the database""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            meal_id VARCHAR(20) PRIMARY KEY,
            meal_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            area VARCHAR(100),
            instructions TEXT,
            ingredients JSONB,
            thumbnail_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)
    conn.commit()
    cursor.close()
    conn.close()


def extract_ingredients(details: dict) -> list[dict]:
    """ Extracts ingredients and their measures from messy JSON format into a structured list of dictionaries. """
    ingredients = []
    for i in range(1, 21): # API is hardcoded to have a max of 20 ingredients
        ingredient = details.get(f"strIngredient{i}")
        measure = details.get(f"strMeasure{i}")
    
        if ingredient and ingredient.strip(): #checks ingredient is not empty
            ingredients.append({
                "ingredient": ingredient.strip(),
                "measure": measure.strip() if measure else "" 
            })

    return ingredients