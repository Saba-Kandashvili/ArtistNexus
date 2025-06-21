# src/core/database_manager.py

import sqlite3
from sqlite3 import Error


class DatabaseManager:
    """
    Handles all database operations for the ArtistNexus application.
    This includes creating the table and adding/retrieving artist data.

    Attributes:
        conn (sqlite3.Connection): The connection object to the database.
    """

    def __init__(self, db_file):
        """
        Initializes the DatabaseManager and connects to the specified database file.

        Args:
            db_file (str): The path to the SQLite database file.
        """
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            print(f"Successfully connected to database: {db_file}")
        except Error as e:
            print(f"Error connecting to database: {e}")

    def create_table(self):
        """
        Creates the main 'artists' table if it doesn't already exist.
        The table stores both the original data and the data fetched from Spotify.
        """
        # Comments explaining each column for your assignment
        create_table_sql = """
                           CREATE TABLE IF NOT EXISTS artists \
                           ( \
                               artist_id \
                               TEXT \
                               PRIMARY \
                               KEY,     -- The unique Spotify ID for the artist \
                               artist_name \
                               TEXT \
                               NOT \
                               NULL,    -- The name of the artist \
                               country \
                               TEXT,    -- The country of origin from the initial dataset \
                               spotify_popularity \
                               INTEGER, -- Popularity score from Spotify (0-100) \
                               spotify_followers \
                               INTEGER, -- Total follower count from Spotify \
                               spotify_genres \
                               TEXT,    -- Comma-separated list of genres from Spotify \
                               last_updated \
                               TEXT \
                               NOT \
                               NULL     -- Timestamp of when the data was last fetched
                           ); \
                           """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            self.conn.commit()
            print("Table 'artists' created or already exists.")
        except Error as e:
            print(f"Error creating table: {e}")

    # We will add more methods here later, like add_artist_data() and get_artist_data()