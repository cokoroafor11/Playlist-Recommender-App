from .feature_build import populate_song_info, one_hot
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def user_playlist_to_dataframe(playlist):
  #Get basic feature df for users
  user_df = populate_song_info(playlist)

  #Sentiment Analysis
  user_df['sentiment'] = user_df['track_name'].apply(lambda row: sent_analysis(row))

  #Normalization
  
  #Get columns to scale
  float_cols = user_df.select_dtypes(include=['float64'])
  scaler = MinMaxScaler()
  float_df = pd.DataFrame(scaler.fit_transform(float_cols), columns = float_cols.columns)
  #Insert scaled columns into df
  user_df= user_df.assign(**dict(float_df.iteritems()))

  ##Key and Popularity Columns

  #Get columns to scale
  pop_key_cols = user_df[['song_popularity','artist_popularity','key']]
  scaler = MinMaxScaler()
  pop_key_df = pd.DataFrame(scaler.fit_transform(pop_key_cols), columns = pop_key_cols.columns)
  #Insert scaled columns into df
  user_df= user_df.assign(**dict(pop_key_df.iteritems()))

  #One hot encoding
  user_df = one_hot(user_df, 'sentiment')
  user_df['sentiment_negative'] = user_df['sentiment_negative'].astype('int')
  user_df['sentiment_neutral']=user_df['sentiment_neutral'].astype('int')
  user_df['sentiment_positive']=user_df['sentiment_positive'].astype('int')

  return user_df
