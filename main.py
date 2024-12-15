from song_storage_tool import add_song
if __name__ == "__main__":

   song_id = add_song("D:\Downloads\Bohemiam_Rhapsody.mp3", "Queen", "Bohemian Rhapsody", "1975-10-31", ["rock", "classic"])
   # while True:
   #     print("\n--- SongStorage Menu ---")
   #     print("1. Adaugă melodie")
   #     print("2. Caută melodii")
   #     print("3. Creează arhivă")
   #     print("4. Șterge melodie")
   #     print("5. Ieșire")
   #
   #     choice = input("Alege o opțiune: ")
   #
   #     if choice == "1":
   #         # Adaugă melodie1
   #         file_path = input("Calea către fișierul melodiei: ")
   #         artist = input("Artist: ")
   #         song_name = input("Numele melodiei: ")
   #         release_date = input("Data apariției (YYYY-MM-DD): ")
   #         tags = input("Lista de tag-uri (separate prin virgulă): ").split(',')
   #
   #         song_id = add_song(file_path, artist, song_name, release_date, tags)
   #         print(f"ID-ul melodiei adăugate: {song_id}")