import pandas as pd
from .config import *
import pymysql
from sqlalchemy import create_engine, text


from .feature_build import populate_song_info, sent_analysis, one_hot
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

def gen_user_playlist_features(playlist):
  #Get basic feature df for users
  user_df = populate_song_info(playlist)

  #Sentiment Analysis
  user_df['sentiment'] = user_df['track_name'].apply(lambda row: sent_analysis(row))

  #Normalization
  ##Float columns
  #Get columns to scale
  float_cols = user_df.select_dtypes(include=['float64'])
  scaler = MinMaxScaler()
  float_df = pd.DataFrame(scaler.fit_transform(float_cols), columns = float_cols.columns)
  #Insert scaled columns into df
  user_df= user_df.assign(**dict(float_df.items()))
  ##Key and Popularity Columns
  #Get columns to scale
  pop_key_cols = user_df[['song_popularity','artist_popularity','key']]
  scaler = MinMaxScaler()
  pop_key_df = pd.DataFrame(scaler.fit_transform(pop_key_cols), columns = pop_key_cols.columns)
  #Insert scaled columns into df
  user_df= user_df.assign(**dict(pop_key_df.items()))

  #One hot encoding
  user_df = one_hot(user_df, 'sentiment')

  #Tfidf genre lists
  tfidf = TfidfVectorizer()
  tfidf_matrix =  tfidf.fit_transform(user_df['genres'].apply(lambda x: " ".join(x)))
  genres_df = pd.DataFrame(tfidf_matrix.toarray())
  genres_df.columns = ['genre' + "_" + i for i in tfidf.get_feature_names_out()]
  genres_df.reset_index(drop = True, inplace=True)
  user_df.drop(columns = ['genres'], inplace = True)
  user_df = pd.concat([user_df,genres_df],axis = 1)
  user_df.dropna(inplace=True)
  return user_df

def get_db_features():
  #Get info from sql
  #Open connection
  connection = pymysql.connect(host= hostname, user= username,password= pw)
  cursor = connection.cursor()
  #create engine
  engine = create_engine('mysql+pymysql://' + username + ':' + pw + '@' + hostname + ':' + str(port) + '/' + db_name , echo=False)
  conn = engine.connect()
  query = text('''SELECT * FROM features''')
  features_df = pd.read_sql(query,conn)

  #Close connection
  cursor.close()
  connection.close()
  features_df.dropna(inplace=True)

  #Sentiment Analysis
  features_df['sentiment'] = features_df['track_name'].apply(lambda row: sent_analysis(row))

  #Normalization
  ##Float columns
  #Get columns to scale
  float_cols = features_df.select_dtypes(include=['float64'])
  scaler = MinMaxScaler()
  float_df = pd.DataFrame(scaler.fit_transform(float_cols), columns = float_cols.columns)
  #Insert scaled columns into df
  features_df= features_df.assign(**dict(float_df.items()))
  ##Key and Popularity Columns
  #Get columns to scale
  pop_key_cols = features_df[['song_popularity','artist_popularity','key']]
  scaler = MinMaxScaler()
  pop_key_df = pd.DataFrame(scaler.fit_transform(pop_key_cols), columns = pop_key_cols.columns)
  #Insert scaled columns into df
  features_df= features_df.assign(**dict(pop_key_df.items()))

  #One hot encoding
  features_df = one_hot(features_df, 'sentiment')

  #Tfidf genre lists
  tfidf = TfidfVectorizer()
  tfidf_matrix =  tfidf.fit_transform(features_df['genres'].apply(lambda x: " ".join(x)))
  genres_df = pd.DataFrame(tfidf_matrix.toarray())
  genres_df.columns = ['genre' + "_" + i for i in tfidf.get_feature_names_out()]
  genres_df.reset_index(drop = True, inplace=True)
  features_df.drop(columns = ['genres'], inplace = True)
  features_df = pd.concat([features_df,genres_df],axis = 1)
  features_df.dropna(inplace=True)
  return features_df

#Get features of songs that aren't in this current playlist
def get_non_playlist_features(features_df, user_playlist_df):
  df_all = features_df.merge(user_playlist_df['song_link'], on=['song_link'],suffixes=('', '_x'), how='left', indicator=True)
  no_playlist_df = df_all[df_all['_merge'] == 'left_only']
  no_playlist_df = no_playlist_df.drop('_merge', axis=1)
  no_playlist_df.drop(list(no_playlist_df.filter(regex = '_x')), axis = 1, inplace = True)
  return no_playlist_df

def generate_recommendations(user_playlist, no_playlist_df,num_recommendations):
  cols = user_playlist.columns.union(no_playlist_df.columns)
  user_playlist = user_playlist.reindex(cols, axis=1, fill_value=0)
  no_playlist_df = no_playlist_df.reindex(cols,axis=1,fill_value=0)
  user_playlist_vector = user_playlist.drop(columns = ['track_name','artists','song_link','playlist_link']).sum()
  no_playlist_df['similarity'] = cosine_similarity(no_playlist_df.drop(columns = ['track_name','artists','song_link','playlist_link']).values,user_playlist_vector.values.reshape(1, -1))[:,0]
  no_playlist_df.sort_values('similarity',ascending = False, inplace = True)
  no_playlist_df.reset_index()
  #return no_playlist_df.drop(columns = ['track_name','artists','link']).values,user_playlist_vector
  return no_playlist_df.head(num_recommendations)[['track_name','artists','song_link','similarity']]