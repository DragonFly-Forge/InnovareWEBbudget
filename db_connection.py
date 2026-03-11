import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# For debugging only: verify the password is being read
# Remove this line before your March 7th presentation

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
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
    # Quick test to see if it works
    conn = get_db_connection()
    if conn:
        print("✅ Connection successful to Design_Finweb!")
        conn.close()