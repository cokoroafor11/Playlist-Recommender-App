#Imports
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

#Save client credentials
client_id = "c1f74565be774e65aa211462aaf5fed8"
client_secret = "2edce4052f8f46639c0e112658572d66"
#Create object
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= client_id,client_secret=client_secret),requests_timeout=100,retries=3)

def extract_songs(playlist):
    #Make sure playlist input is string
    if type(playlist) != str: 
        playlist = str(playlist)
    
    results = spotify.playlist_items(playlist)
    tracks = results['items']
    uris = []
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])

    #Append tracks to list if no type error
    for elem in tracks:
        try:
            uris.append(elem['track']['uri'])
        except TypeError:
            continue
    return uris

def get_track_info(track):
    track = spotify.track(track)
    track_info = {}
    artists= []
    track_info['name'] = track['name']
    for artist in track['artists']:
        artists.append(artist['name'])
    track_info['artists'] = artists
    track_info['popularity'] = track['popularity']
    return track_info

def populate_song_info(playlist):
    '''
    Function that populates an dictionary where keys are the audio features and values are an array of scores for each song
    This function performs the lionshare of data setup
    '''
    songlist = extract_songs(playlist)

    #Storage for various types of data
    song_data = {}
    name_array = []
    artist_array = []
    popularity_array = []
    dance_array = []
    energy_array = []
    key_array = []
    loudness_array = []
    mode_array = []
    speech_array = []
    acoustic_array = []
    instrument_array = []
    live_array = []
    valence_array = []
    tempo_array = []
    link_array = []
    
    #Loop to append song info to appropriate array
    for song in songlist:
        
        features = spotify.audio_features(song)[0]
        #Check if features don't exist, skip the song entry
        if features ==  None:
            continue
        
        #Get song names, artists, popularity
        track = get_track_info(song)
        name_array.append(track['name'])
        artist_array.append(track['artists'])
        popularity_array.append(track['popularity'])

        #Append feature to each corresponding array
        dance_array.append(features['danceability'])
        energy_array.append(features['energy'])
        key_array.append(features['key'])
        loudness_array.append(features['loudness'])
        mode_array.append(features['mode'])
        speech_array.append(features['speechiness'])
        acoustic_array.append(features['acousticness'])
        instrument_array.append(features['instrumentalness'])
        live_array.append(features['liveness'])
        valence_array.append(features['valence'])
        tempo_array.append(features['tempo'])
        link_array.append(song)
        
    #Put all song data in a library with proper labels
    song_data['track_name'] = name_array
    song_data['artists'] = artist_array
    song_data['popularity'] = popularity_array
    song_data['danceability'] = dance_array
    song_data['energy'] = energy_array
    song_data['key'] = key_array
    song_data['loudness'] = loudness_array
    song_data['mode'] = mode_array
    song_data['speechiness'] = speech_array
    song_data['acousticness'] = acoustic_array
    song_data['instrumentalness'] = instrument_array
    song_data['liveness'] = live_array
    song_data['valence'] = valence_array
    song_data['tempo'] = tempo_array
    song_data['link'] = link_array
    
    song_db = pd.DataFrame(song_data)
    return song_db

def excel_list_to_df():
    '''Create the dataframe from the excel sheet of playlists'''

    df = pd.read_excel("Spotify Playlists 1 per genre.xlsx")
    playlists = df['Link']
    return playlists

print(extract_songs('https://open.spotify.com/playlist/7IKIjt9wZPPQWgvHo1SeFO?si=b2e74ab95f0f45cd'))