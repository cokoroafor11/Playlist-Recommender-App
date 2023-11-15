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
    user_features = gen_user_playlist_features(link)
    db_features = get_db_features()
    songs = generate_recommendations(user_features,db_features,20)
    data = songs.to_html()
    return render_template('recommendations.html', data=data)