import json
import os
from fastapi import FastAPI, HTTPException, Query
import psycopg2
from pyscopg2.extras import RealDictCursor

#instance of FastAPI web app
app = FastAPI(title="Meal Recipe API", description="API display layer for recipes ingested into PostgreSQL database.")

#retrieve environment variables for db connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
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

