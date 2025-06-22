import pandas as pd
import time
from datetime import datetime

from .api_handler import APIHandler
from .db_manager import DatabaseManager


class DataProcessor:
    """
    data processing

    loads data from a CSV file, uses the APIHandler to combine it
    with live data from Spotify, and then uses the DatabaseManager to store
    the results in a SQLite database.

    attributes:
        api_handler (APIHandler)
        db_manager (DatabaseManager)
    """

    def __init__(self, api_handler: APIHandler, db_manager: DatabaseManager):
        """
        attributes:
            api_handler (APIHandler)
            db_manager (DatabaseManager)
        """
        self.api_handler = api_handler
        self.db_manager = db_manager

    def process_and_store_artists(self, csv_filepath):
        """
        main method for data processing

        reads the CVS file row by row, fetches data from the API, and stores it in the database.

        this should be run by a thread

        args:
            csv_filepath (str)
        """
        print("Starting the data processing pipeline...")
        try:
            # read the artist data from the CSV file (pandas)
            df = pd.read_csv(csv_filepath)
            print(f"Successfully loaded {len(df)} artists from {csv_filepath}.")
        except FileNotFoundError:
            print(f"Error: The file {csv_filepath} was not found.")
            return  # stop if the file doesn't exist

        # loop through rows
        for index, row in df.iterrows():
            artist_id = row['artist_id']
            artist_name_from_csv = row['artist_name']
            country = row['country']
            # if spotify doesnt have the genre use the cvs one
            genre_from_csv = row['artist_genre']

            print(f"\nProcessing artist {index + 1}/{len(df)}: {artist_name_from_csv} ({artist_id})")

            details = self.api_handler.get_artist_details(artist_id)

            if details:

                details['artist_id'] = artist_id
                details['country'] = country
                details['last_updated'] = datetime.now().isoformat()

                # spotify returns a list of images. take index one (about 300x300)
                # first, check if the list is empty
                if details.get('images') and len(details['images']) > 1:
                    details['image_url'] = details['images'][1]['url']
                else:
                    details['image_url'] = None # no image available

                details.pop('images', None)


                self.db_manager.add_artist(details)

                time.sleep(0.1)
            else:
                print(f"Skipping database entry for {artist_name_from_csv} due to API error.")

        print("\n--- Data processing pipeline finished! ---")