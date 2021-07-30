# Estaciones
Got a pile of "Liked" songs in your Spotify?

One of those people who can't be bothered to create intricate playlists? Wish you didn't have to keep skipping tracks until you find a song you like?

Same.

This script will group your "Liked" Spotify songs into seasons (which are defined somewhat arbitrarily) and create a playlist for each season.

## Running

1. [Create a Spotify integration](https://developer.spotify.com/dashboard/login), and add a re-direct URL (it doesn't have to be a real OAuth2 redirect URL, any URL you control is fine, even localhost)
2. Create 3 new env variables: `SPOTIPY_CLIENT_ID` set to your Spotify client ID, `SPOTIPY_CLIENT_SECRET` set to your client secret, and `SPOTIPY_REDIRECT_URL` set to __exactly__ the URL you chose in step 1.
3. Install the dependencies with `pip install -r requirements.txt`
4. Run `main.py`. 

Use this script at your own risk to your Spotify playlists library. This script won't delete anything, but errors will create empty playlists that you have to delete one-by-one.

### Name
_Estación_ (_estaciones_, plural) in Spanish means both "station" (as in radio station) and season (as in time of year). 