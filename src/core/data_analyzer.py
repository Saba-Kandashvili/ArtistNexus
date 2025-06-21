# src/core/data_analyzer.py

import pandas as pd
import sqlite3
from .base_manager import BaseManager # <-- IMPORT THE PARENT CLASS

class DataAnalyzer(BaseManager):
    """
    Performs data analysis on the artist data stored in the database.

    This class reads data from the database into a Pandas DataFrame and provides
    methods to compute various statistics required for plotting.

    Attributes:
        db_path (str): The file path to the SQLite database.
        df (pd.DataFrame): The DataFrame holding all artist data.
    """

    def __init__(self, db_path):
        """
        Initializes the DataAnalyzer and loads data from the database.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        self.df = None
        self.load_data()

    def load_data(self):
        """
        Loads all data from the 'artists' table in the SQLite database
        into a Pandas DataFrame.
        """
        try:
            # Establish a connection to the database
            conn = sqlite3.connect(self.db_path)
            # Use Pandas' read_sql_query for efficient data loading
            self.df = pd.read_sql_query("SELECT * FROM artists", conn)
            conn.close()
            print(f"DataAnalyzer loaded {len(self.df)} records from the database.")
        except Exception as e:
            print(f"Error loading data from database: {e}")
            # Initialize an empty DataFrame on failure
            self.df = pd.DataFrame()

    def get_top_n_countries_by_followers(self, n=15):
        """
        Calculates the total number of followers for all artists from each country
        and returns the top N countries.

        Args:
            n (int): The number of top countries to return.

        Returns:
            pd.Series: A Pandas Series with country as the index and the sum
                       of followers as values, sorted descending. Returns None on error.
        """
        if self.df.empty or 'country' not in self.df or 'spotify_followers' not in self.df:
            print("Cannot perform analysis: DataFrame is empty or missing required columns.")
            return None

        # Group by country, sum the followers, sort, and take the top N
        top_countries = self.df.groupby('country')['spotify_followers'].sum().sort_values(ascending=False).head(n)
        return top_countries

    def get_top_n_countries_by_avg_popularity(self, n=15):
        """
        Calculates the average artist popularity for each country and returns the top N.

        Args:
            n (int): The number of top countries to return.

        Returns:
            pd.Series: A Pandas Series with country as the index and the mean
                       popularity as values, sorted descending. Returns None on error.
        """
        if self.df.empty or 'country' not in self.df or 'spotify_popularity' not in self.df:
            print("Cannot perform analysis: DataFrame is empty or missing required columns.")
            return None

        # Group by country, calculate the mean popularity, sort, and take the top N
        top_countries_avg_pop = self.df.groupby('country')['spotify_popularity'].mean().sort_values(
            ascending=False).head(n)
        return top_countries_avg_pop

    # We will add more analysis methods here later, like for genres.