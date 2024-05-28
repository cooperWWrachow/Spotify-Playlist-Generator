from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import base64

app = Flask(__name__)

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

def get_access_token() -> str:
    # grab token dictionary
    token_info = sp_oauth.get_cached_token() # dictionary
    if token_info is None:
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
    else:
        access_token = token_info['access_token']
    return access_token

def get_color(colors: list[str]) -> str:
    while True:
        print("Red | Yellow | Green | Blue | Purple | Orange | Black")
        color = input("Please enter a color: ").strip().lower()
        if color in colors:
            return color
        else:
            print("Invalid color. Please enter a valid color.")

# requests artists names from user based on number of artists. passes artists through info function for name + ID
def artists_confirm (sp: object, num: int) -> list[dict]:
    artist_names = []
    
    for i in range(0, num):
        artist = input("Enter Name: ")
        artist_names.append(artist)
        # final names of artists
    artist_ids = []

    # pass each name into info function to get id too
    for name in artist_names:
        artist_id = get_artist_info(sp, name)
        artist_ids.append(artist_id)

    return artist_ids

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

def get_user_albums(numArr: list[str], albums: list[str]) -> list[str]:
    # holds final list of album ids
    album_id_lis = []
    # Iterate over user selected numbers
    for num in numArr:
        # Convert to int because dictionary header is int
        num = int(num)
        # Iterate over albums
        for album in albums:
            # if album number matches then append
            if num in album:
                album_id_lis.append(album[num][1]) 
                break
    return album_id_lis

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
        track_values = sp.audio_features(track)
        # d = track_values[0]['danceability']
        e = track_values[0]['energy']
        v = track_values[0]['valence']
        t = track_values[0]['tempo']
        element = {track: ({"e":e}, {"v":v}, {"t":t})}
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
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback(): 

    #  grab access token
    access_token = get_access_token()
    sp = spotipy.Spotify(auth=access_token)


    colors = ["red", "blue","yellow","green","orange","purple","black"]
    color = get_color(colors)

    # retrieve user input (neglecting spaces right now)
    num = int(input("How many artists would you like to add? (1 or more): "))
    print("When using spaces, surround entire name with quotes!!!")
    print("The more specific the better the more accurate the results.")

    stop = True
    while (stop):
        artist_ids = []
        artist_names = []
        # EX: [{ID: NAME}, {ID2: NAME}, ...]
        artist_info = artists_confirm(sp, num)
        for info in artist_info:
            for key, value in info.items():
                print(value)
                artist_names.append(value)
                artist_ids.append(key)
        # print(artist_info)
        confirmation = input("are these the correct artist (y/n)? ").lower()
        if confirmation == 'y' or confirmation == 'yes':
            stop = False
        if stop == True:
            print("Please re-enter your artist more specifically.")

    # get each artists' albums
    albums = get_artists_albums(sp, artist_ids)
    # display proper key value pair to user excluding ID. ie.; 1: album name
    for album in albums:
        for key, value in album.items():
            album_num = key
            album_name = value[0]
            print(f"{album_num}: {album_name}")
    # print(albums)

    # get user album numbers in an array
    album_nums = input("Enter the numbers of each corresponding album (spaces in between): ")
    final_nums = album_nums.split()


    album_id_lis = get_user_albums(final_nums, albums)

    all_tracks = get_album_track_ids(sp, album_id_lis)

    all_tracks_values = get_track_values(sp, all_tracks)

    # gets final tracks for playlist
    passing_tracks = []
    for track in all_tracks_values:
        # grab desired values for the track and pass thru test function
        for tID, tVal in track.items():
            e = tVal[0]['e']
            v = tVal[1]['v']
            # print(f"{d}, {e}, {v}, {t}")
            result = color_test(color, e, v)
            # if track succeeds then append to list
            if (result):
                passing_tracks.append(tID)

    create_playlist(sp, artist_names, passing_tracks, color)

    return "Authenticated successfully!"



if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.1.128', port=5000)

