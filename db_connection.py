import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env if it exists (for local development)
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    
    # 1. Check if Render's single DATABASE_URL exists
    database_url = os.getenv("postgresql://web_budget_user:XtrhEkOHMSAl83VUniUvSM3PeWT4ximU@dpg-d6ohq8ma2pns738ed210-a/web_budget_URL")
    
    try:
        if database_url:
            # If on Render, use the URL and force SSL
            connection = psycopg2.connect(database_url, sslmode='require')
        else:
            # Fallback to your local .env variables
            connection = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT")
            )
        return connection
    except Exception as error:
        print(f"❌ Error connecting to database: {error}")
        return None

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("✅ Connection successful!")
        conn.close()