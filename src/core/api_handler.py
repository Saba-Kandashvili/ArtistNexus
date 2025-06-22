import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class APIHandler:
    """
    communication with spotify Web API
    """

    def __init__(self, client_id, client_secret):
        self.sp = None
        self.is_authenticated = False
        try:
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.is_authenticated = True
            print("API Handler authenticated successfully with Spotify.")
        except Exception as e:
            print(f"Error authenticating with Spotify: {e}")
            self.is_authenticated = False

    def get_artist_details(self, artist_id):
        """
        detailed info about a single artist
        """
        if not self.is_authenticated:
            print("Cannot fetch artist details: API Handler is not authenticated.")
            return None

        try:
            artist_data = self.sp.artist(artist_id)

            details = {
                'artist_name': artist_data['name'],
                'spotify_popularity': artist_data['popularity'],
                'spotify_followers': artist_data['followers']['total'],
                'spotify_genres': ', '.join(artist_data['genres']),
                'images': artist_data['images'],
                'external_urls': artist_data['external_urls']
            }

            if not artist_data.get('images'):
                print(f"Warning: No images found for artist: {artist_data['name']} (ID: {artist_id})")
            elif len(artist_data['images']) < 2:
                print(f"Note: Only {len(artist_data['images'])} image(s) found for artist: {artist_data['name']} (ID: {artist_id})")

            return details

        except spotipy.exceptions.SpotifyException as e:
            print(f"Error: Artist with ID '{artist_id}' not found on Spotify. Details: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred when fetching data for artist ID '{artist_id}': {e}")
            return None