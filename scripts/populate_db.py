# scripts/populate_database.py (Ultra-Safe and Stable Version)

import sys
import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import time

# --- Path Setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.core.api_handler import APIHandler
from src.core.db_manager import DatabaseManager
import config

# --- ULTRA-SAFE THROTTLING PARAMETERS ---
# Based on logs, we need to be extremely conservative.
# Let's use a very small number of concurrent workers.
MAX_WORKERS = 3

# We will enforce a significant delay between each request to ensure
# we never hit the per-second rate limit. 0.35s = ~3 requests/sec max.
# REQUEST_INTERVAL = 0.35
REQUEST_INTERVAL = 0.25

# --- Global, thread-safe instances ---
api_handler = APIHandler(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)


# In scripts/populate_database.py, replace the process_single_artist function

def process_single_artist(artist_row, db_path):
    """
    Worker function with a built-in delay to ensure safe API usage.
    """
    try:
        # Enforce the delay at the start of every task.
        time.sleep(REQUEST_INTERVAL)

        # Unpack data
        artist_id = artist_row['artist_id']
        artist_name = artist_row['artist_name']

        # API Call
        details = api_handler.get_artist_details(artist_id)
        if not details:
            return f"API error for {artist_name}. Skipping."

        # Data Enrichment
        if not details['spotify_genres']: details['spotify_genres'] = artist_row['artist_genre']
        details.update({
            'artist_id': artist_id, 'country': artist_row['country'],
            'last_updated': datetime.now().isoformat(),
            'image_url': details['images'][1]['url'] if details.get('images') and len(details['images']) > 1 else None,
            # --- NEW LOGIC for Spotify URL ---
            'spotify_url': details['external_urls']['spotify'] if details.get('external_urls') else None
        })
        # We no longer need these complex objects
        details.pop('images', None)
        details.pop('external_urls', None)

        # Database Write
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        sql = '''INSERT OR REPLACE INTO artists(artist_id, artist_name, country, spotify_popularity, spotify_followers, spotify_genres, image_url, spotify_url, last_updated)
                 VALUES(:artist_id, :artist_name, :country, :spotify_popularity, :spotify_followers, :spotify_genres, :image_url, :spotify_url, :last_updated)'''
        cursor.execute(sql, details)
        conn.commit()
        conn.close()

        return f"OK: {artist_name}"
    except Exception as e:
        return f"ERROR: {artist_name} - {e}"


# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- Starting ULTRA-SAFE Database Population Script ---")
    print(f"Concurrent workers: {MAX_WORKERS}, Request interval: {REQUEST_INTERVAL * 1000:.0f}ms")

    db_manager = DatabaseManager(db_file=config.DATABASE_NAME)
    if not db_manager.is_connected(): sys.exit("Halting: Database failed to initialize.")

    try:
        csv_file_path = os.path.join(project_root, 'data', 'artist_data.csv')
        df = pd.read_csv(csv_file_path).dropna(subset=['artist_id', 'artist_name', 'country', 'artist_genre'])
        artists_to_process = [row for index, row in df.iterrows()]
        total_artists = len(artists_to_process)
        print(f"Loaded {total_artists} valid artists to process.")
    except FileNotFoundError:
        sys.exit(f"FATAL: The file {csv_file_path} was not found.")

    processed_count = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_single_artist, artist, config.DATABASE_NAME): artist for artist in
                   artists_to_process}

        for future in as_completed(futures):
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"Progress: {processed_count}/{total_artists} artists processed...")

    print(f"\n--- Population Script Finished! All {total_artists} artists have been processed. ---")