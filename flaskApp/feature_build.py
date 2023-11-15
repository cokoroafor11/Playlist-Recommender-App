#Imports

import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import time
import pymysql
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from .config import *
#Save file variables
#playlists_file = './datasets/all_spotify_playlists.xlsx'
playlist_df = pd.read_excel("all_spotify_playlists.xlsx")
#spotify_feature_file = 'spotify_features.xlsx'



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

def get_artist_info(track):
    '''Helper function for get_track_info function'''
    artist_info = {}
    artist_id = track["artists"][0]["id"]
    artist = spotify.artist(artist_id)
    artist_pop = artist["popularity"]
    artist_genres = artist["genres"]

    artist_info['artist_genres'] = artist_genres
    artist_info['artist_popularity'] = artist_pop
    return artist_info

def get_track_info(track):
    track = spotify.track(track)
    track_info = {}
    artists= []
    artist_info = get_artist_info(track)
    track_info['name'] = track['name']
    for artist in track['artists']:
        artists.append(artist['name'])
    track_info['artists'] = artists
    track_info['popularity'] = track['popularity']
    return track_info, artist_info

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
    song_pop_array = []
    artist_pop_array = []
    genres_array = []
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
    song_link_array = []
    
    #Loop to append song info to appropriate array
    for song in songlist:
        
        features = spotify.audio_features(song)[0]
        #Check if features don't exist, skip the song entry
        if features == None:
            continue
        
        #Get song names, artists, popularity, and genres
        track, artist = get_track_info(song)
        name_array.append(track['name'])
        artist_array.append(track['artists'])
        song_pop_array.append(track['popularity'])
        artist_pop_array.append(artist['artist_popularity'])
        genres_array.append(artist['artist_genres'])
        
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
        song_link_array.append(song)
        
    #Put all song data in a library with proper labels
    song_data['track_name'] = name_array
    song_data['artists'] = artist_array
    song_data['song_popularity'] = song_pop_array
    song_data['artist_popularity'] = artist_pop_array
    song_data['genres'] = genres_array
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
    song_data['song_link'] = song_link_array
    
    song_db = pd.DataFrame(song_data)
    song_db['playlist_link'] = playlist
    return song_db

def excel_list_to_df():
    '''Create the dataframe from the excel sheet of playlists'''

    df = pd.read_excel("Spotify Playlists 1 per genre.xlsx")
    playlists = df['Link']
    return playlists

def sent_analysis(song_title):
  '''
  The sentiment analysis outputs positive, negative, neutral scores
  Combines into compound score that is a combo of all the above
  We will use the compound score, then put it into one of three buckets
  '''
  analyzer = SentimentIntensityAnalyzer()
  analysis = analyzer.polarity_scores(song_title)['compound']
  if analysis < -0.5:
    return 'negative'
  elif analysis > 0.5:
    return 'positive'
  else:
    return 'neutral'

def one_hot(df, column):
  if type(column) != str: column = str(column)
  df = pd.get_dummies(df, columns=[column])
  return df

def feature_engineering(df):
    df['sentiment'] = df['track_name'].apply(lambda row: sent_analysis(row))
    
    #Normalization
    
    ##Float columns
    float_cols = df.select_dtypes(include=['float64'])
    scaler = MinMaxScaler()
    float_df = pd.DataFrame(scaler.fit_transform(float_cols), columns = float_cols.columns)
    
    #Insert scaled columns into df
    df= df.assign(**dict(float_df.items()))

    ##Key and Popularity Columns
    pop_key_cols = df[['song_popularity','artist_popularity','key']]
    scaler = MinMaxScaler()
    pop_key_df = pd.DataFrame(scaler.fit_transform(pop_key_cols), columns = pop_key_cols.columns)
    
    #Insert scaled columns into df
    df= df.assign(**dict(pop_key_df.items()))

    #One hot encoding
    df = one_hot(df, 'sentiment')
    df['sentiment_negative'] = df['sentiment_negative'].astype('int')
    df['sentiment_neutral']=df['sentiment_neutral'].astype('int')
    df['sentiment_positive']=df['sentiment_positive'].astype('int')

    return df

def build_feature_frame(playlist_df):
    playlists = list(playlist_df['Spotify Playlist ID'])
    #feature_dfs = []

    #Open connection
    connection = pymysql.connect(host= hostname, user= username,password= pw)
    cursor = connection.cursor()
    #create engine
    engine = create_engine('mysql+pymysql://' + username + ':' + pw + '@' + hostname + ':' + str(port) + '/' + db_name , echo=False)
    
    #Iterate through playlists and push these dataframes to sql
    for playlist in playlists:
        time.sleep(20)
        print('playlist {} started'.format(playlist))

        try:
            features = populate_song_info(playlist)
            features['artists'] = features['artists'].astype(str)
            features['genres'] = features['genres'].astype(str)

        except spotipy.SpotifyException:
            continue
        #push df to sql
        features.to_sql('features', engine, if_exists='append',index = False, chunksize=100000, method='multi')
        

    #Close connection
    cursor.close()
    connection.close()
        

    #Concatenate dataframes together before export 

if __name__ == "__main__":
    build_feature_frame(playlist_df)
