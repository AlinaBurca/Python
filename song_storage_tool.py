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

class SongStorage:
    def __init__(self):
        self.conn=psycopg2.connect(**DB_CONFIG)
        self.cursor=self.conn.cursor()
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)


    def add_song(self, song_path, artist, song_name, release_date, tags):

        if not os.path.exists(song_path):
            print("Error: File does not exist.")
        try:
            file_name = os.path.basename(song_path)
            print("basename: ", file_name)
            destination = os.path.join(STORAGE_DIR, file_name)
            print("dest: ", destination)
            shutil.copy(song_path, destination)

            self.cursor.execute("""
                INSERT INTO songs (file_name, artist, song_name, release_date, tags)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """, (file_name, artist, song_name, release_date, tags))
            song_id = self.cursor.fetchone()[0]

            self.conn.commit()
            print(f"The song was added with ID: {song_id}")
            return song_id

        except Exception as e:
            print(f"Error adding the song: {e}")


    def delete_song (self, song_id):
        try:
            self.cursor.execute("SELECT file_name FROM songs WHERE id=%s", (song_id,))
            result=self.cursor.fetchone()
            if result:
                song=result[0]
                print("song: ", song)
                if os.path.exists(os.path.join(STORAGE_DIR, song)):
                    os.remove(os.path.join(STORAGE_DIR, song))
                else:
                    print("Error: File not found.")
                self.cursor.execute("DELETE FROM songs WHERE id=%s", (song_id,))
                self.conn.commit()
                print("Song deleted successfully.")
            else:
                print("Song id was not found.")
        except Exception as e:
            print(f"Error deleting the song : {e}")

    def modify_data(self, song_id, **args):
        try:
            for key, value in args.items():
                self.cursor.execute(f"UPDATE songs SET {key}=%s WHERE id=%s", (value, song_id))
            self.conn.commit()
            print("Data modified successfully.")
        except Exception as e:
            print(f"Error modifying the data: {e}")

