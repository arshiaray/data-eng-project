import os
import psycopg2
import requests
import json
import time

#db connection credentials from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_PORT = os.getenv("DB_PORT", "2323")
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
    """Creates the meals table in PostgreSQL DB."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
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
    """
    
    cursor.execute(query)
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


def fetch_categories() -> list[str]: #free api has a request limit, so category is the best way to get bulk meal recipes
    """Fetches a list of all the categories in the MealDB API"""
    url = "https://www.themealdb.com/api/json/v1/1/list.php?c=list"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to get categories list from API. Status: {response.status_code}")
        return []

    data = response.json()
    categories_dict = data.get("meals", []) #fetches dict of a dict of categories

    # Extract category names into a list
    categories = [cat["strCategory"] for cat in categories_dict if cat.get("strCategory")]
    print (f" Discovered {len(categories)} categories from API: {', '.join(categories)}")

    return categories


def fetch_store_meals(category: str, cursor, upsert_query): 
    """Fetches and upserts meals for one category"""
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    print(f"Processing category: {category}...")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Skipping category {category} due to API error. Status: {response.status_code}")
        return 0

    meals_summary = response.json().get("meals", [])
    if not meals_summary:
        print(f"No meals found for category {category}.")
        return 0

    meals_processed = 0
    for meal in meals_summary:
        meal_id = meal["idMeal"]
        detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
        detail_response = requests.get(detail_url)

        if detail_response.status_code != 200:
            print(f"Skipping meal {meal_id} due to API error. Status: {detail_response.status_code}")
            continue
        else:
            details = detail_response.json().get("meals", [{}])[0] #API returns a list of one dict, so we take the first element
            ingredients_list = extract_ingredients(details)

            cursor.execute(upsert_query, (
                details.get("idMeal"),
                details.get("strMeal"),
                details.get("strCategory"),
                details.get("strArea"),
                details.get("strInstructions"),
                json.dumps(ingredients_list),  # Convert list of dicts to JSON string
                details.get("strMealThumb"),
                ),
            )
            meals_processed += 1

            #small delay to avoid spamming the API with requests
            time.sleep(0.1)

    print(f"Finished processing category: {category}. Processed {meals_processed} recipes.")
    return meals_processed

    
def main_pipeline():
    """Main pipeline function that discovers categories and ingests all the recipes into the database."""
    initialise_db()

    categories = fetch_categories()
    if not categories:
        print("No categories found. Pipeline terminating.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()

    upsert_query = """
        INSERT INTO meals (meal_id, meal_name, category, area, instructions, ingredients, thumbnail_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (meal_id) DO UPDATE SET
            meal_name = EXCLUDED.meal_name,
            category = EXCLUDED.category,
            area = EXCLUDED.area,
            instructions = EXCLUDED.instructions,
            ingredients = EXCLUDED.ingredients,
            thumbnail_url = EXCLUDED.thumbnail_url;
    """

    total_records = 0
    for category in categories:
        count = fetch_store_meals(category, cursor, upsert_query)
        total_records += count
        conn.commit()  # Commit after each category to save progress

    cursor.close()
    conn.close()
    print(f"\nPipeline complete! Successfully ingested/updated {total_records} total recipes across all categories.")

    
if __name__ == "__main__":
    main_pipeline()