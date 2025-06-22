import pandas as pd
import sqlite3
from .base_manager import BaseManager


class DataAnalyzer(BaseManager):
    def __init__(self, db_path):
        super().__init__(db_path)
        self.df = None
        self.load_data()

    def load_data(self):
        """
        loads data from the 'artists' table
        """
        try:
            conn = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query("SELECT * FROM artists", conn)
            conn.close()
            print(f"DataAnalyzer loaded {len(self.df)} records from the database.")
        except Exception as e:
            print(f"Error loading data from database: {e}")
            self.df = pd.DataFrame()

    def get_available_countries(self):
        if self.df.empty: return []
        # drop missing values just for this calculation
        return sorted(self.df['country'].dropna().unique())

    def get_top_n_countries_by_followers(self, n=15):
        if self.df.empty: return None
        # filtering specific to this analysis
        analysis_df = self.df.dropna(subset=['country', 'spotify_followers'])
        return analysis_df.groupby('country')['spotify_followers'].sum().sort_values(ascending=False).head(n)

    def get_top_n_countries_by_avg_popularity(self, n=15):
        if self.df.empty: return None
        analysis_df = self.df.dropna(subset=['country', 'spotify_popularity'])
        return analysis_df.groupby('country')['spotify_popularity'].mean().sort_values(ascending=False).head(n)

    def get_genre_distribution_for_country(self, country: str, n=10):
        if self.df.empty: return None
        analysis_df = self.df.dropna(subset=['country', 'spotify_genres'])
        if country not in analysis_df['country'].values: return None

        country_df = analysis_df[analysis_df['country'] == country]
        genres = country_df['spotify_genres'].str.split(', ').explode()
        return genres.value_counts().head(n)

    def get_popularity_vs_followers(self, country: str):
        if self.df.empty: return None, None
        analysis_df = self.df.dropna(subset=['country', 'spotify_followers', 'spotify_popularity'])
        if country not in analysis_df['country'].values: return None, None

        country_df = analysis_df[analysis_df['country'] == country]
        return country_df['spotify_followers'], country_df['spotify_popularity']

    def get_popularity_distribution(self):
        if self.df.empty: return None
        return self.df['spotify_popularity'].dropna()

    def get_most_popular_artist_in_country(self, country: str):
        if self.df.empty:
            return None

        # country and spotify_popularity mustn ot be null
        required_columns = ['country', 'spotify_popularity']

        # check if they exist
        if not all(col in self.df.columns for col in required_columns):
            return None

        # filter by non-null country and popularity
        analysis_df = self.df.dropna(subset=required_columns)
        if country not in analysis_df['country'].values:
            return None

        country_df = analysis_df[analysis_df['country'] == country]
        if country_df.empty:
            return None

        most_popular_idx = country_df['spotify_popularity'].idxmax()
        return self.df.loc[most_popular_idx].to_dict()

