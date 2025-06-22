# scripts/populate_database.py (The Final "Safe Mode" Version)

import sys
import os
import pandas as pd
from datetime import datetime
import time

# weird path stuff
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.core.api_handler import APIHandler
from src.core.db_manager import DatabaseManager
import config

if __name__ == "__main__":
    print("--- Starting SAFE MODE Database Population Script ---")
    print("This script runs in a single thread to guarantee we do not hit API rate limits.")

    # 1. Initialize Handlers
    api_handler = APIHandler(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)
    db_manager = DatabaseManager(db_file=config.DATABASE_NAME)

    if not db_manager.is_connected() or not api_handler.is_authenticated:
        sys.exit("Halting: Database or API failed to initialize.")

    # load data
    try:
        csv_file_path = os.path.join(project_root, 'data', 'artist_data.csv')
        df = pd.read_csv(csv_file_path).dropna(subset=['artist_id', 'artist_name', 'country', 'artist_genre'])
        artists_to_process = [row for index, row in df.iterrows()]
        total_artists = len(artists_to_process)
        print(f"Loaded {total_artists} valid artists to process.")
    except FileNotFoundError:
        sys.exit(f"FATAL: The file {csv_file_path} was not found.")

    # no threading or i get banned from spotify api  ):
    for i, artist_row in enumerate(artists_to_process):
        try:
            # print progress
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{total_artists} artists processed...")

            # limit or i get banned :[
            time.sleep(0.5)

            artist_id = artist_row['artist_id']
            artist_name = artist_row['artist_name']

            details = api_handler.get_artist_details(artist_id)
            if not details:
                print(f"Warning: API error for {artist_name}. Skipping.")
                continue

            if not details['spotify_genres']: details['spotify_genres'] = artist_row['artist_genre']

            image_url = None
            if details.get('images'):
                if len(details['images']) > 0:
                    # index 1 images = medium size
                    image_index = 1 if len(details['images']) > 1 else 0
                    image_url = details['images'][image_index]['url']

            details.update({
                'artist_id': artist_id, 'country': artist_row['country'],
                'last_updated': datetime.now().isoformat(),
                'image_url': image_url,
                'spotify_url': details['external_urls']['spotify'] if details.get('external_urls') else None
            })
            details.pop('images', None)
            details.pop('external_urls', None)

            # save to db
            db_manager.add_artist(details)

        except Exception as e:
            print(f"An unexpected error occurred for artist {artist_row.get('artist_name', 'N/A')}: {e}")

    print(f"\n--- Population Script Finished! All {total_artists} artists have been processed. ---")