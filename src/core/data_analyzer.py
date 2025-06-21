# src/core/data_analyzer.py (Upgraded Version)

import pandas as pd
import sqlite3
from .base_manager import BaseManager


class DataAnalyzer(BaseManager):
    """
    Performs data analysis on the artist data stored in the database.
    """

    def __init__(self, db_path):
        super().__init__(db_path)
        self.df = None
        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query("SELECT * FROM artists", conn)
            # Drop rows where crucial data might be missing for cleaner analysis
            self.df.dropna(subset=['country', 'spotify_followers', 'spotify_popularity', 'spotify_genres'],
                           inplace=True)
            conn.close()
            print(f"DataAnalyzer loaded {len(self.df)} records from the database.")
        except Exception as e:
            print(f"Error loading data from database: {e}")
            self.df = pd.DataFrame()

    def get_available_countries(self):
        """Returns a sorted list of unique countries from the dataframe."""
        if self.df.empty:
            return []
        return sorted(self.df['country'].unique())

    def get_top_n_countries_by_followers(self, n=15):
        if self.df.empty: return None
        return self.df.groupby('country')['spotify_followers'].sum().sort_values(ascending=False).head(n)

    def get_top_n_countries_by_avg_popularity(self, n=15):
        if self.df.empty: return None
        return self.df.groupby('country')['spotify_popularity'].mean().sort_values(ascending=False).head(n)

    # --- NEW ANALYSIS METHODS ---

    def get_genre_distribution_for_country(self, country: str, n=10):
        """
        Calculates the top N genre distribution for a specific country.
        """
        if self.df.empty or country not in self.df['country'].values:
            return None

        country_df = self.df[self.df['country'] == country]
        # This is a powerful pandas trick: split the genre string and create new rows
        genres = country_df['spotify_genres'].str.split(', ').explode()
        # Count the occurrences and get the top N
        return genres.value_counts().head(n)

    def get_popularity_vs_followers(self, country: str):
        """
        Returns the popularity and followers data for a scatter plot for a given country.
        """
        if self.df.empty or country not in self.df['country'].values:
            return None, None

        country_df = self.df[self.df['country'] == country]
        return country_df['spotify_followers'], country_df['spotify_popularity']

    def get_popularity_distribution(self):
        """Returns the popularity column for a histogram."""
        if self.df.empty:
            return None
        return self.df['spotify_popularity']