import os
import shutil

import psycopg2

DB_CONFIG = {
    'dbname': 'SongStorage',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

STORAGE_DIR = "./Storage"

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def add_song(file_path, artist, song_name, release_date, tags):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        file_name = os.path.basename(file_path)
        print("basename: ", file_name)
        destination = os.path.join(STORAGE_DIR, file_name)
        print("dest: ", destination)
        shutil.copy(file_path, destination)

        cursor.execute("""
            INSERT INTO songs (file_name, artist, song_name, release_date, tags)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (file_name, artist, song_name, release_date, tags))
        song_id = cursor.fetchone()[0]

        conn.commit()
        print(f"The song was added with ID: {song_id}")
        return song_id

    except Exception as e:
        print(f"Error adding the song: {e}")
    finally:
        cursor.close()
        conn.close()

