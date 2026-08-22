<h3> ARCHITECTURE </h3>
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

<p> </p>
