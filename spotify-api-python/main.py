import time
from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import base64

app = Flask(__name__)
app.secret_key = "236910"

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID="05df09b03e7d4f82b868e3a3ac4d769c"
CLIENT_SECRET="344f2abfa80f4b67955feff1bc0fe659"

# Set up Spotipy client with user authorization
scope = "user-top-read playlist-modify-public playlist-modify-private ugc-image-upload"
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri="http://localhost:5000/callback",
                        scope=scope)

# redirect_uri="http://192.168.1.128:5000/callback",

# retrieve access token from the session 
def get_access_token() -> str:
    token_info = session.get('token_info', None)

    if not token_info:
        return None
    # check expiration date (may not be needed in future)
    now = int(time.time())
    is_token_expired = token_info['expires_at'] - now < 60

    if is_token_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return token_info['access_token']

# takes in an artist name and returns the ID of the artist
def get_artist_info(sp: object, name: str) -> dict:
    artist_dict = sp.search(q=name, type='artist', limit=10)

    artists = artist_dict['artists']['items']

    final = artists[0]
    artist_id = final['id']
    artist_name = final['name']

    return {artist_id: artist_name}

# takes in a list of ID's and returns an array containing a number 
# and corresponsing albums for user
def get_artists_albums(sp: object, IDarr: list[str]) -> list[dict]:
    artist_albums = []
    # artist = IDarr[0]
    count = 1 # will be used as label for user
    for artist in IDarr:
        albums = sp.artist_albums(artist, album_type='album')
        for album in albums['items']:
            cur = album['name']
            temp = album['id']
            # Sometimes singles bypass album_type='album', so this check bypasses those
            ttype = album['album_group']
            if ttype != 'album':
                continue
            else:
                # append count number and album name
                artist_albums.append({count:(cur, temp, ttype)})
                count += 1
    return artist_albums

# search for each album and create list of song ID's
def get_album_track_ids(sp: object, IDarr: list[str]) -> list[str]:
    all_tracks = []
    for album_id in IDarr:
        track_item = sp.album_tracks(album_id)['items']
        for track in track_item:
            cur = track['id']
            all_tracks.append(cur)
    return all_tracks

def get_track_values(sp: object, IDarr: list[str]) -> list[dict]:
    tracks_values = []
    for track in IDarr:
    # track = IDarr[0]
        track_features = sp.audio_features(track)
        e = track_features[0]['energy']
        v = track_features[0]['valence']
        element = {track: ({"e":e}, {"v":v})}
        tracks_values.append(element)
    return tracks_values

# matches with correct color and then checks if song succeeds the values of that color
def color_test (color: str, e:float, v:float) -> bool:
    match color:
        case "blue":
            if (0.2 < v < 0.6 and e < 5):
                return True
            else:
                return False
        case "red":
            if (e > 0.7):
                return True
            else:
                return False
        case "green":
            if (0.3 < e < 0.7 and 0.4 < v > 0.7):
                return True
            else:
                return False
        case "orange":
            if (e > 0.65 and v > 0.6):
                return True
            else:
                return False
        case "yellow":
            if (0.3 < e < 0.7 and v > 0.7):
                return True
            else:
                return False
        case "black":
            if (v < 0.4):
                return True
            else:
                return False
        case "purple":
            if (0.3 < v < 0.7 and e < 0.7):
                return True
            else:
                return False


def create_playlist(sp: object, nameArr: list[str], idArr: list[str], color: str):
    acr = ""
    desc = ""
    image_path = f"covers/{color}.jpg"

    for name in nameArr:
        acr += name[0]
        desc += f"{name} "

    title = f"{color.upper()}: {acr}"

    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user=user_id, name=title, public=True, description=desc)
    pID = playlist['id']

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    
    sp.playlist_upload_cover_image(pID, encoded)

    sp.user_playlist_add_tracks(user_id, pID, idArr)

    return 


# when we go to base route, we run ths index function which authorizes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        token_info = sp_oauth.get_cached_token() # dictionary
        if token_info is None:
            code = request.args.get('code')
            token_info = sp_oauth.get_access_token(code)

        # handles deprecation warning between dict and string for future refernece
        if isinstance(token_info, dict):
            # If token_info is a dictionary, store it in the session as usual
            session['token_info'] = token_info
        else:
            # If token_info is a string (future behavior), get the full token info from cache
            session['token_info'] = sp_oauth.get_cached_token()

        return redirect(url_for('color'))
    except Exception as e:
        error = f"An unexpected error has occurred during the authentication process: {str(e)}"
        return render_template('error.html', error=error)

@app.route('/color-picker', methods=['GET', 'POST'])
def color(): 
    access_token = get_access_token()
    if not access_token:
        return redirect(url_for('login'))

    colors = ["red", "blue","yellow","green","orange","purple","black"]

    # sp = spotipy.Spotify(auth=access_token)
    if request.method == 'POST':
        user_color = request.form['user-color'].strip().lower()
        artist_count = request.form['artist-count'].strip()
        
        # error checking for both inputs 
        if user_color not in colors:
            error = "Please enter a valid color from above."
            return render_template('color-picker.html', error=error)
        
        if not artist_count.isdigit() or int(artist_count) < 1:
            error = "Enter 1 or more artists please."
            return render_template('color-picker.html', error=error)

        # store values in the session
        session['user_color'] = user_color
        session['artist_count'] = artist_count

        return redirect(url_for('artists'))
    
    return render_template('color-picker.html')

@app.route('/choose-artists', methods=['GET', 'POST'])
def artists():

    access_token = get_access_token()
    if not access_token:
        return redirect(url_for('login'))

    # retrive artist count from session
    count = int(session['artist_count'])
    
    # creates list of user submitted artists and puts in session
    artists = []
    if request.method == 'POST':
        for num in range(count):
            artists.append(request.form[f'artist-{num}'])
        
        session['user_artists'] = artists

        return redirect(url_for('confirm'))

    # passed count to the template (jinja2)
    return render_template('choose-artists.html', count=count)


@app.route('/artist-confirmation')
def confirm():
    try:
        access_token = get_access_token()
        if not access_token:
            return redirect(url_for('login'))
        
        sp = spotipy.Spotify(auth=access_token)

        user_artists = session['user_artists']

        info = []
        # pass each name into info function to get id too
        for name in user_artists:
            artist_info = get_artist_info(sp, name)
            info.append(artist_info)
        
        # create list of just names for html
        artists_names = []
        artist_ids = []
        for i in info:
            for key, value in i.items():
                artists_names.append(value)
                artist_ids.append(key)

        session['confirmed_names'] = artists_names
        session['artists_ids'] = artist_ids

        return render_template('artist-confirmation.html', names=artists_names)
    except Exception as e:
        error = f"An unexpected error has occurred while retrieving the artists: {str(e)}"
        session.clear()
        return render_template('error.html', error=error)

@app.route('/choose-albums', methods=['GET', 'POST'])
def albums():
    try:
        access_token = get_access_token()
        if not access_token:
            return redirect(url_for('login'))
        
        sp = spotipy.Spotify(auth=access_token)

        artists_ids = session['artists_ids']
        # EX: {1: (name, id, type)}
        album_info = get_artists_albums(sp, artists_ids)
        
        albums = []
        ids = []
        for album in album_info:
            for key, value in album.items():
                # two lists (albums is just album names)

                albums.append(value[0])
                ids.append({key: value[1]})

        # store album ids
        session['album_ids'] = ids

        if request.method == 'POST':
            # getlist grabs list of indexes
            user_albums  = request.form.getlist('artist-albums')
            # store user choices from multiselect
            session['user_choices'] = user_albums
            return redirect(url_for('success'))
                
        return render_template('choose-albums.html', albums=albums)
    except Exception as e:
        error = f"An unexpected error has occurred while retrieving the albums: {str(e)}"
        session.clear()
        return render_template('error.html', error=error)


@app.route('/success')
def success():
    try:
        access_token = get_access_token()
        if not access_token:
            return redirect(url_for('login'))
        
        sp = spotipy.Spotify(auth=access_token)

        user_color = session['user_color']
        artist_names = session['confirmed_names']

        final_albums = []
        ids = session['album_ids']
        choices = session['user_choices']
        for i in ids:
            for k,v in i.items():
                for choice in choices:
                    if choice == k:
                        final_albums.append(v)
                    else:
                        continue
        
        # grab each track from all albums
        all_tracks = get_album_track_ids(sp, final_albums)
        
        # get energy and valence for each track
        all_tracks_values = get_track_values(sp, all_tracks)

        # gets final tracks for playlist
        passing_tracks = []
        for track in all_tracks_values:
            # grab desired values for the track and pass thru test function
            for tID, tVal in track.items():
                e = tVal[0]['e']
                v = tVal[1]['v']
                result = color_test(user_color, e, v)
                # if track succeeds then append to list
                if (result):
                    passing_tracks.append(tID)
                else:
                    continue
        
        if passing_tracks == []:
            error = "No Songs matched the color. Please try again and be more specific."
            session.clear()
            return render_template('error.html', error=error)
        
        create_playlist(sp, artist_names, passing_tracks, user_color)

        session.clear()

        return render_template('success.html')
    except Exception as e:
        error = f"An unexpected error has occurred while generating your playlist: {str(e)}"
        session.clear()
        return render_template('error.html', error=error)



if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.1.168', port=5000)

