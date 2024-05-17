from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID="05df09b03e7d4f82b868e3a3ac4d769c"
CLIENT_SECRET="344f2abfa80f4b67955feff1bc0fe659"

# Set up Spotipy client with user authorization
scope = "user-top-read"  # Scope for reading user's top artists
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri="http://localhost:5000/callback",
                        scope=scope)

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    sp = spotipy.Spotify(auth=access_token)
    
    top_artists = get_top_artists(sp)
    if top_artists:
        print("Your top 5 most listened to artists:")
        for index, artist in enumerate(top_artists):
            print(f"{index+1}. {artist['name']}")
    
    return "Authenticated successfully!"

def get_top_artists(sp, limit=5):
    result = sp.current_user_top_artists(limit=limit, time_range='long_term')
    return result['items']

if __name__ == '__main__':
    app.run(debug=True)