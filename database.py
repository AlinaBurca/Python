import psycopg2
import logging
import os
from  dotenv import load_dotenv

"""Configure logging to display detailed execution information."""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""Load environment variables from the .env file."""
load_dotenv()

"""Database configuration."""
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def connect_db():
    """
     Connects to the database using the configuration provided in the DB_CONFIG dictionary.

    Returns:
        conn: A connection object to the database.

    Raises:
        Exception: If the connection to the database fails.
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error("Failed to connect to database: %s", e)
        raise

def setup_database():
    """
    Sets up the database by creating the songs table if it does not exist.

    Table structure:
      -id: Serial primary key
      -file_name: File name (TEXT), required.
      -artist: Artist name (TEXT), optional.
      -song_name: Song name (TEXT), optional.
      -release_date: Release date (DATE), optional.
      -tags: Tags (TEXT[]), optional

    The function closes the connection upon completion and logs the status.

    """
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id SERIAL PRIMARY KEY,
                file_name TEXT NOT NULL,
                artist TEXT,
                song_name TEXT,
                release_date DATE,
                tags TEXT[]
            );
        """)
        conn.commit()
    conn.close()
    logging.info("Database setup completed.")

if __name__ == "__main__":
    setup_database()


