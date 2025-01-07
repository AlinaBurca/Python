import os
import shutil
import pygame
import psycopg2
from dotenv import load_dotenv
import logging

"""Configure logging to display detailed execution information."""
logging.basicConfig(
    filename="songstorage.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

"""Storage directory for songs."""
STORAGE_DIR = "./Storage"


class SongStorage:
    """

    A class to manage song storage and perform various operations on songs as
    adding, deleting, modifying, searching, creating save lists, and playing songs.
    """
    def __init__(self):
        """ Initializes the database connection and creates the storage directory if it does not exist."""

        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
        logging.info("Initialized SongStorage and ensured storage directory exists.")

    def add_song(self, song_path, artist, song_name, release_date, tags):
        """
        Add a new song to the database and copy the song file to the storage directory.

        Args:
          song_path (str): The path to the song file.
          artist (str): The artist of the song.
          song_name (str): The name of the song.
          release_date (str): The release date of the song in the format 'YYYY-MM-DD'.
          tags (list): A list of tags associated with the song.

        Returns:
            int: The ID of the added song in the database if successful.
        """
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
            self.conn.rollback()
            logging.error(f"Error adding the song: {e}")

    def delete_song(self, song_id):
        """
        Delete a song from the database and remove the corresponding file from the storage directory.

        Args:
            song_id (int): The ID of the song to be deleted.

        """
        try:
            song_id = int(song_id)
            logging.info(f"Attempting to delete song with ID: {song_id}")

            self.cursor.execute("SELECT * FROM songs WHERE id=%s", (song_id,))
            result = self.cursor.fetchone()

            if result:
                song = result[1]
                song_path = os.path.join(STORAGE_DIR, song)

                if os.path.exists(song_path):
                    os.remove(song_path)
                    logging.info(f"Deleted file: '{song_path}'.")
                else:
                    logging.warning(f"File '{song_path}' not found during deletion.")

                self.cursor.execute("DELETE FROM songs WHERE id=%s", (song_id,))
                self.conn.commit()
                logging.info(f"Deleted song with ID {song_id} from database.")
            else:
                logging.warning(f"Song ID {song_id} not found in database.")
        except ValueError:
            logging.error(f"Invalid song ID provided: {song_id}. It must be an integer.")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error deleting the song: {e}")

    def modify_data(self, song_id, **args):
        """
        Modify the metadata of a song in the database.

        Args:
            song_id (int): The ID of the song to be modified.
            **args: The key-value paris of the fields to be modified.
        """
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
            self.conn.rollback()
            logging.error(f"Error modifying the data: {e}")

    def search_song(self, artist, song_format):
        """
        Search for songs by artist and file format.

        Args:
          artist (str): The artist of the song.
          song_format (str): The format of the song file (e.g., 'mp3', 'wav').

        Returns:
          list: List of songs matching the search criteria.
        """
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
            self.conn.rollback()
            logging.error(f"Error searching the song: {e}")

    def create_savelist(self, output_path, artist, song_format):
        """
        Create a savelist of songs by an artist with a specific file format.

        Args:
         output_path (str): The path to save the savelist archive.
         artist (str): The artist of the songs.
         song_format (str): The format of the song files (e.g., 'mp3', 'wav').

        """
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
        """
        Play a song by its ID using Pygame.

        Args:
          song_id (int): The ID of the song to be played.

        """
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
            self.conn.rollback()
            logging.error(f"Error playing the song: {e}")
        finally:
            pygame.mixer.quit()
            logging.info("Pygame resources released.")
