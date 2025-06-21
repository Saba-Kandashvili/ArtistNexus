# src/core/db_manager.py (More Robust Version)

import sqlite3
from sqlite3 import Error

class DatabaseManager:
    """
    Handles all database operations for the ArtistNexus application.
    This includes creating the table and adding/retrieving artist data.
    """

    def __init__(self, db_file):
        """
        Initializes the DatabaseManager and connects to the specified database file.
        """
        self.conn = None
        try:
            # Connect to the database and get a connection object
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            print(f"Successfully connected to database: {db_file}")
            # Immediately attempt to create the table upon successful connection
            self.create_table()
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None # Ensure conn is None if connection fails

    def is_connected(self):
        """Returns True if the database connection is active."""
        return self.conn is not None

    def create_table(self):
        """
        Creates the main 'artists' table if it doesn't already exist.
        This is now called automatically during initialization.
        """
        if not self.is_connected():
            print("Cannot create table: No database connection.")
            return

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS artists (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT NOT NULL,
            country TEXT,
            spotify_popularity INTEGER,
            spotify_followers INTEGER,
            spotify_genres TEXT,
            last_updated TEXT NOT NULL
        );
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            self.conn.commit()
            print("Table 'artists' is ready.")
        except Error as e:
            print(f"Error creating table: {e}")

    def add_artist(self, artist_details: dict):
        """
        Inserts or replaces an artist's data in the database.
        """
        if not self.is_connected():
            print("Cannot add artist: No database connection.")
            return

        sql = ''' INSERT OR REPLACE INTO artists(artist_id, artist_name, country, spotify_popularity, spotify_followers, spotify_genres, last_updated)
                  VALUES(:artist_id, :artist_name, :country, :spotify_popularity, :spotify_followers, :spotify_genres, :last_updated) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, artist_details)
            self.conn.commit()
            # We can make this print less verbose to clean up the output
            # print(f"Successfully added/updated '{artist_details['artist_name']}' in the database.")
        except Error as e:
            print(f"Error adding artist '{artist_details['artist_name']}' to database: {e}")