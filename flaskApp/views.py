from .user_input import user_playlist_to_dataframe

from flask import render_template, request
from flaskApp import app


#Home page
@app.route('/home')
def home():
    return render_template('index.html')


#Recs page

@app.route('/recommendations', methods = ['POST'])
def recommendations():
    link = request.form['URL']
    user_df = user_playlist_to_dataframe(link)

    return render_template('recommendations.html',data=user_df.to_html())
