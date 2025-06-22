# src/core/db_manager.py (More Robust Version)

import sqlite3
from sqlite3 import Error

class DatabaseManager:
    """
    database operations
    """

    def __init__(self, db_file):
        """
        connects to the db
        """
        self.conn = None
        try:
            # connect
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            print(f"Successfully connected to database: {db_file}")
            # create table
            self.create_table()
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def is_connected(self):
        """a method to check if the db is connected or not"""
        return self.conn is not None

    def create_table(self):
        """
        cretae table if it doesnt exist
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
            image_url TEXT,
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
        insert artist's data
        """
        if not self.is_connected():
            print("Cannot add artist: No database connection.")
            return

        sql = ''' INSERT OR REPLACE INTO artists(artist_id, artist_name, country, spotify_popularity, spotify_followers, spotify_genres, image_url, last_updated)
                  VALUES(:artist_id, :artist_name, :country, :spotify_popularity, :spotify_followers, :spotify_genres, :image_url, :last_updated) '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, artist_details)
            self.conn.commit()
        except Error as e:
            print(f"Error adding artist '{artist_details['artist_name']}' to database: {e}")