# src/core/api_handler.py

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class APIHandler:
    """
    Handles all communication with the Spotify Web API.

    This class is responsible for authenticating with the API and fetching
    data for artists. It is designed to be independent of the database or UI.

    Attributes:
        sp (spotipy.Spotify): The authenticated Spotipy client object.
        is_authenticated (bool): True if authentication was successful, False otherwise.
    """

    def __init__(self, client_id, client_secret):
        """
        Initializes the APIHandler and authenticates with Spotify.

        Args:
            client_id (str): The Spotify Client ID.
            client_secret (str): The Spotify Client Secret.
        """
        self.sp = None
        self.is_authenticated = False
        try:
            # Set up the authentication manager using the Client Credentials Flow
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

            # Create the main Spotipy object that we will use for all API calls
            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            self.is_authenticated = True
            print("API Handler authenticated successfully with Spotify.")
        except Exception as e:
            # This handles errors like invalid credentials or network issues during auth
            print(f"Error authenticating with Spotify: {e}")
            self.is_authenticated = False

    def get_artist_details(self, artist_id):
        """
        Fetches detailed information for a single artist from the Spotify API.

        This method encapsulates the API call and includes error handling.
        It returns a structured dictionary of the data we care about.

        Args:
            artist_id (str): The unique Spotify ID for the artist to look up.

        Returns:
            dict: A dictionary containing the artist's details (name, popularity,
                  followers, genres) if successful.
            None: If the artist is not found or an API error occurs.
        """
        # First, check if we failed to authenticate in the constructor
        if not self.is_authenticated:
            print("Cannot fetch artist details: API Handler is not authenticated.")
            return None

        try:
            # The main API call to fetch artist data
            artist_data = self.sp.artist(artist_id)

            # If the call is successful, extract the specific pieces of data we need
            details = {
                'artist_name': artist_data['name'],
                'spotify_popularity': artist_data['popularity'],
                'spotify_followers': artist_data['followers']['total'],
                # Spotify returns genres as a list, so we join them into a single string
                'spotify_genres': ', '.join(artist_data['genres'])
            }
            return details

        except spotipy.exceptions.SpotifyException as e:
            # This specific exception is often for a '404 Not Found' error
            print(f"Error: Artist with ID '{artist_id}' not found on Spotify. Details: {e}")
            return None
        except Exception as e:
            # A catch-all for other potential issues (e.g., network timeout)
            print(f"An unexpected error occurred when fetching data for artist ID '{artist_id}': {e}")
            return None