import os
import shutil
import pygame
import psycopg2
from dotenv import load_dotenv
import logging


logging.basicConfig(
    filename="songstorage.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

STORAGE_DIR = "./Storage"

class SongStorage:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
        logging.info("Initialized SongStorage and ensured storage directory exists.")

    def add_song(self, song_path, artist, song_name, release_date, tags):
        if not os.path.exists(song_path):
            logging.error("Error: File does not exist.")
            return
        try:
            file_name = os.path.basename(song_path)
            destination = os.path.join(STORAGE_DIR, file_name)
            shutil.copy(song_path, destination)

            self.cursor.execute("""
                INSERT INTO songs (file_name, artist, song_name, release_date, tags)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """, (file_name, artist, song_name, release_date, tags))
            song_id = self.cursor.fetchone()[0]

            self.conn.commit()
            logging.info(f"Added song '{song_name}' with ID {song_id}.")
            return song_id
        except Exception as e:
            logging.error(f"Error adding the song: {e}")

    def delete_song(self, song_id):
        try:
            self.cursor.execute("SELECT * FROM songs WHERE id=%s", song_id)
            result = self.cursor.fetchone()
            print("Result ", result
            )
            if result:
                song = result[1]
                song_path = os.path.join(STORAGE_DIR, song)
                if os.path.exists(song_path):
                    os.remove(song_path)
                    logging.info(f"Deleted file '{song_path}'.")
                else:
                    logging.warning(f"File '{song_path}' not found during deletion.")
                self.cursor.execute("DELETE FROM songs WHERE id=%s", (song_id,))
                self.conn.commit()
                logging.info(f"Deleted song with ID {song_id} from database.")
            else:
                logging.warning(f"Song ID {song_id} not found in database.")
        except Exception as e:
            logging.error(f"Error deleting the song: {e}")

    def modify_data(self, song_id, **args):
        try:
            self.cursor.execute("SELECT file_name FROM songs WHERE id=%s", (song_id,))
            result = self.cursor.fetchone()
            if not result:
                logging.warning(f"Song ID {song_id} not found for modification.")
                return
            for key, value in args.items():
                self.cursor.execute(f"UPDATE songs SET {key}=%s WHERE id=%s", (value, song_id))
            self.conn.commit()
            logging.info(f"Modified data for song ID {song_id} with changes: {args}")
        except Exception as e:
            logging.error(f"Error modifying the data: {e}")

    def search_song(self, artist, song_format):
        try:
            query = "SELECT * FROM songs WHERE artist=%s AND file_name LIKE %s"
            self.cursor.execute(query, (artist, f"%.{song_format}"))
            result = self.cursor.fetchall()
            if not result:
                logging.info(f"No songs found for artist '{artist}' with format '{song_format}'.")
                return
            logging.info(f"Found {len(result)} song(s) for artist '{artist}' with format '{song_format}'.")
            return result
        except Exception as e:
            logging.error(f"Error searching the song: {e}")

    def create_savelist(self, output_path, artist, song_format):
        songs = self.search_song(artist, song_format)
        if not songs:
            logging.warning("No songs found for savelist creation.")
            return
        try:
            for song in songs:
                file_name = song[1]
                song_path = os.path.join(STORAGE_DIR, file_name)
                if os.path.exists(song_path):
                    shutil.copy(song_path, output_path)
                    logging.info(f"Copied song '{file_name}' to '{output_path}'.")
                else:
                    logging.warning(f"File '{file_name}' not found for savelist.")
            archive = shutil.make_archive(output_path, 'zip', output_path)
            logging.info(f"Archive created at '{archive}'.")
        except Exception as e:
            logging.error(f"Error creating the savelist: {e}")

    def play_song(self, song_id):
        try:
            self.cursor.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
            result = self.cursor.fetchone()
            if not result:
                logging.warning(f"Song ID {song_id} not found.")
                return

            song = result[1]
            song_path = os.path.abspath(os.path.join(STORAGE_DIR, song))

            if os.path.exists(song_path):
                logging.info(f"Playing song '{song_path}'.")
                pygame.mixer.init()
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    user_input = input("Press 'q' to stop playback: ")
                    if user_input.lower() == 'q':
                        pygame.mixer.music.stop()
                        logging.info("Playback stopped by user.")
                        break
            else:
                logging.warning(f"File '{song_path}' not found for playback.")
        except KeyboardInterrupt:
            pygame.mixer.music.stop()
            logging.info("Playback stopped manually by user.")
        except Exception as e:
            logging.error(f"Error playing the song: {e}")
