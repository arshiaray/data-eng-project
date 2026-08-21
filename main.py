import json
import os
from fastapi import FastAPI, HTTPException, Query
import psycopg2
from psycopg2.extras import RealDictCursor

#instance of FastAPI web app
app = FastAPI(title="Meal Recipe API", description="API display layer for recipes ingested into PostgreSQL database.")

#retrieve environment variables for db connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "2323")
DB_NAME = os.getenv("DB_NAME", "meal_db")
DB_USER = os.getenv("DB_USER", "my_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "my_password")

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor #returns results as dictionaries instead of tuples
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


#check endpoint connection 
@app.get("/")
def read_root():
    return {"message": "Recipe API is live and connected to PostgreSQL!"}

#recipe collection endpoint
@app.get("/recipes")
def get_recipes(category: str = None, limit: int =10):
    """Fetches recipes from the DB based on an optional category and a limit"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if category:
        query = "SELECT meal_id, meal_name, category, area, thumbnail_url FROM meals WHERE LOWER(category) = LOWER(%s) LIMIT %s;"
        cursor.execute(query, (category, limit))
    else:
        query = "SELECT meal_id, meal_name, category, area, thumbnail_url FROM meals LIMIT %s;"
        cursor.execute(query, (limit,))

    recipes = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"count": len(recipes), "recipes": recipes}


#single recipe endpoint
@app.get("/recipes/{meal_id}")
def get_recipe_by_id(meal_id: str):
    """Fetches full details for a single recipe based on its meal_id"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM meals WHERE meal_id = %s;"
    cursor.execute(query, (meal_id,))
    recipe = cursor.fetchone()

    cursor.close()
    conn.close()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

