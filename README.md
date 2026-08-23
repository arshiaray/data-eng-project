<u><h3> ARCHITECTURE </h3></u>
<p> This project is a simple, end-to-end data pipeline that fetches recipe data from an API, stores it in a database and makes it available through a web API.</p>

<p>[External Recipe API] --> [Ingestion Script] --> [Postgresql DB] --> [FastAPI Rest Layer]</p>

<h4>1. Data Ingestion (ingest.py)</h4>
<ul>
<li>Downloads raw recipe data in a JSON format from external TheMealDB API.</li>
<li>Selects the useful fields and formats them.</li>
<li>Saved the data into a PostgreSQL DB. It skips recipes that are already ingested to avoid duplication if ran again.</li>
</ul>

<h4>2. Database (PostgreSQL)</h4>
<ul>
<li>Stores the cleaned recipes in a 'meals' table.</li>
<li>Uses 'meal_id' as a primary key so each recipe is unique and easy to find.</li>
</ul>

<h4>3. Web API (main.py)</h4>
<ul>
<li>Built with FastAPI to serve the data over HTTP.</li>
<li>'/recipes': returns a list of recipes. Supports filtering by categories (such as 'seafood' or 'vegetarian') and setting a limit on how many recipes to return.</li>
<li>'recipes/{meal_id}': Looks up and returns full details for one specific recipe.</li>
<li>Includes safety checks so database connections close properly and errors return clear error messages instead of crashing the app.</li>
</ul>

<h4>4. Deployment (Docker & Render)</h4>
<ul>
<li>Docker: Wraps the app code so it runs the exact same way on a local server as it does in the cloud.</li>
<li>Render: Hosts the database and API online for free so that anyone can test the endpoints live.</li>
</ul>
<p> </p>
<u><h3>STATUS AND SYSTEM CAPABILITIES</h3></u>
<h4>What Works</h4>

<ul>
<li><b>Data Ingestion: </b>'ingest.py' fetches raw JSON from The MealDB API, extracts key fields, and loads them safely into PostgreSQL.</li>
<li><b>Idempotent Data Loads: </b>Re-running the ingestion script safely skips existing records ('ON CONFLICT DO NOTHING') without throwing primary key errors.</li>
<li><b>Recipe Filtering API:</b> 'GET /recipes' returns formatted JSON data and supports optional 'category' filtering (case-insensitive) and custom `limit` parameters.</li>
<li><b>Single Recipe Lookup:</b> 'GET /recipes/{meal_id}' fetches full details for a specific recipe and returns a structured `404 Not Found` error if the ID doesn't exist.</li>
<li><b>Database Safety and Error Handling:</b> Explicit connection handling ('try/except/finally' blocks) prevents database connection leaks and returns clean HTTP `500` JSON errors if PostgreSQL becomes unreachable.</li>
<li><b>Automated Cloud Deployment:</b> Fully containerised with Docker and live on Render with automated deployments on every 'Git Push'</li>
</ul>

<h4>Considerations</h4>
<ul>
<li><b>Render Free Tier Start Ups:</b> Due to the API being hosted on Render's free tier, the web service winds down after 15 minutes of inactivity. The first request after an idle period takes around 30 seconds to a minute to respond while the container wakes up. Fortunately, the data is retained even when the web service goes to sleep.</li>
</ul>

<u><h3>HOW TO RUN</h3></u>
<h4>Option 1: Live Cloud Demo (No Installation Required)</h4>
