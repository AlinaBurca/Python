import psycopg2
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    "dbname": "SongStorage",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": 5432
}

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error("Failed to connect to database: %s", e)
        raise

def setup_database():
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
