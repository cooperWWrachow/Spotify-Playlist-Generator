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

# when we go to base route, we run ths index function which authorizes
@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # retrieve user input (neglecting spaces right now)
    artist_names = []
    num = int(input("How many artists would you like to add? (1 or more): "))
    print("When using spaces, surround entire name with quotes!!!")
    for i in range(0, num):
        artist = input("Enter Name: ")
        artist_names.append(artist)

    access_token = get_access_token()
    sp = spotipy.Spotify(auth=access_token)

    # get artist id's 
    artist_ids = []
    for name in artist_names:
        artist_id = get_artist_id(sp, name)
        artist_ids.append(artist_id)

    # print(artist_ids)

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
    # print(album_id_lis)

    all_tracks = get_album_track_ids(sp, album_id_lis)
    print(all_tracks)

    
    # reduce album list 

    return "Authenticated successfully!"

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

# takes in an artist name and returns the ID of the artist
def get_artist_id(sp: object, name: str) -> str:
    artist_dict = sp.search(q=name, type='artist', limit=2)
    # more accurate when i retrieve the top 2 of the search, for some reason when 
    # limit to 1 it gives wrong person
    two_artists = artist_dict['artists']['items']
    # print(two_artists)
    main_art = two_artists[0]
    # print(main_art)
    artist_id = main_art['id']
    
    return artist_id

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

# def get_artists_tracks(sp, IDarr):
    
#     artist_id = IDarr[0]
#     all_tracks = []
#     # Retrieve albums of the artist
#     albums = sp.artist_albums(artist_id, album_type='album')
#     for album in albums['items']:
#         # Retrieve tracks of each album
#         tracks = sp.album_tracks(album['id'])
#         for track in tracks['items']:
#             all_tracks.append(track['id'])
#     return all_tracks

if __name__ == '__main__':
    app.run(debug=True)

