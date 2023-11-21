from .recommendations import gen_user_playlist_features,get_db_features,generate_recommendations

from flask import render_template, request
from flaskApp import app


#Home page
@app.route('/home')
def home():
    return render_template('index.html')


#Recs page
@app.route('/recommendations', methods=['POST'])
def recommendations():
    link = request.form['URL']
    #user_features = gen_user_playlist_features(link)
    db_features = get_db_features()
    #songs = generate_recommendations(user_features,db_features,20)
    songs =db_features.head(15) 
    songs.rename(columns = {'track_name': 'Track Name', 'artists': 'Artists', 'song_link': 'Song Link'})
    data = songs[['track_name','artists','song_link']].to_html(render_links=True, escape=False)
    
    return render_template('recommendations.html', data=data)

#About page
@app.route('/about')
def about():
    return render_template('about.html')

#Instructions page
@app.route('/instructions')
def instructions():
    return render_template('instructions.html')