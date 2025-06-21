# src/core/data_processor.py

import pandas as pd
import time
from datetime import datetime

# We are importing the other classes we created within our 'core' package
from .api_handler import APIHandler
from .db_manager import DatabaseManager


class DataProcessor:
    """
    Orchestrates the data processing pipeline.

    This class loads data from a CSV file, uses the APIHandler to enrich it
    with live data from Spotify, and then uses the DatabaseManager to store
    the results in a SQLite database.

    Attributes:
        api_handler (APIHandler): An instance of the API handler.
        db_manager (DatabaseManager): An instance of the database manager.
    """

    def __init__(self, api_handler: APIHandler, db_manager: DatabaseManager):
        """
        Initializes the DataProcessor.

        Args:
            api_handler (APIHandler): An already initialized API handler instance.
            db_manager (DatabaseManager): An already initialized database manager instance.
        """
        self.api_handler = api_handler
        self.db_manager = db_manager

    def process_and_store_artists(self, csv_filepath):
        """
        The main method to run the entire data processing pipeline.

        It reads a CSV, iterates through rows, fetches data from Spotify API,
        and saves it to the database. This function is designed to be the
        target for a thread.

        Args:
            csv_filepath (str): The full path to the input CSV file.
        """
        print("Starting the data processing pipeline...")
        try:
            # Step 1: Read the artist data from the CSV file using Pandas
            df = pd.read_csv(csv_filepath)
            print(f"Successfully loaded {len(df)} artists from {csv_filepath}.")
        except FileNotFoundError:
            print(f"Error: The file {csv_filepath} was not found.")
            return  # Stop execution if the file doesn't exist

        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            artist_id = row['artist_id']
            artist_name_from_csv = row['artist_name']
            country = row['country']
            # Get the genre from the CSV as a fallback
            genre_from_csv = row['artist_genre']

            print(f"\nProcessing artist {index + 1}/{len(df)}: {artist_name_from_csv} ({artist_id})")

            details = self.api_handler.get_artist_details(artist_id)

            if details:
                # NEW LOGIC: Check if Spotify returned genres. If not, use the CSV genres.
                if not details['spotify_genres']:  # This checks for an empty string
                    print(f"-> Spotify has no genres for {artist_name_from_csv}. Using genres from dataset.")
                    details['spotify_genres'] = genre_from_csv

                details['artist_id'] = artist_id
                details['country'] = country
                details['last_updated'] = datetime.now().isoformat()

                self.db_manager.add_artist(details)

                time.sleep(0.1)
            else:
                print(f"Skipping database entry for {artist_name_from_csv} due to API error.")

        print("\n--- Data processing pipeline finished! ---")