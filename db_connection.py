import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env if it exists (for local development)
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    
    # Use the KEY name you set in Render's dashboard (DATABASE_URL)
    database_url = os.getenv("DATABASE_URL")
    
    try:
        if database_url:
            # If on Render, it will find the URL and connect
            connection = psycopg2.connect(database_url, sslmode='require')
            return connection
        else:
            # Fallback for your local laptop testing
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "web_budget"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT", "5432")
            )
            return connection
    except Exception as error:
        print(f"❌ Error connecting to database: {error}")
        return None