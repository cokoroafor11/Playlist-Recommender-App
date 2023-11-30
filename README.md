# Song Recommender Application

The song recommender app provides user song recommendations based on their Spotify playlist input.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following:


```bash
pip install spotipy
pip install vaderSentiment
pip install pymysql
pip install sqlalchemy
pip install flask
```

## Set Up
1. You will need to create an [Amazon Web Services RDS](https://aws.amazon.com/rds/) database. If you already have an account, you will be prompted to log in. Otherwise, you will need to create one. AWS offers a free tier that will work just fine for this application (around 5000 song capacity for the db). Obviously if you want to add more entries beyond this, you'll have to pay for a higher tier. Now, there are many tutorials out there about how to set up a database instance, so find what works best for you, but the one I loosely followed was [this](https://www.youtube.com/watch?v=Ng_zi11N4_c). You'll need to note down information about the database including the username, password, hostname, and database name, as those will be needed for the config file.  **Note: Make sure you set up a MySQL instance, as this is what the application runs on.**

2. Additionally, you will need to go to [Spotify for Developers](https://developer.spotify.com/) and create a new application. This is where you will get the credentials (ID and Secret) for the config file needed to run the application.

The config file should look as follows:

```python
#AWS Database Instance Identifier
username = #username used for the db
password = #passowrd for the db
hostname = #hostname for db
db_name = #name of db
port = #Usually 3306

client_id = #client ID pulled from the app you created
client_secret = #client secret pulled from the app you created
```

## Usage
### Building the database
- There is a file named feature_build.py in the flaskApp folder
- This file, when run, will create and populate a database with song features based on the user's given database info
- The playlists are pulled from an excel sheet called "all_spotify_playlists.xlsx"
- If you would like to recommend from specific playlists, you can update this playlist with the playlists you would like to pull songs from
- Once you run the feature build file, you should have  a populated database that you can pull song information from. I would recommend testing this to ensure it works.

### Running the application through webpage
The webpage isn't hosted anymore because I ran out of AWS Free Tier use for the year. I plan to re-host next year. However, you can still use it locally. To do so, do the following:
1. Run ```python flask --app flaskApp run --debug``` in your terminal
2. Once this is run, the home page is located at http://127.0.0.1:5000/home. From here, you should be seeing this.
![Song Recommender Screenshot](/photos/"song-recommender-pic.PNG"?raw=true "Song Recommender Screenshot")




## Future Work
1. Creating a script to run updates on the database every week. The idea here is to update only with songs that are recently added to playlists, skewing towards newer music.

2. Adding drop down button to allow user to select the number of song recommendations they want

3. I plan to update the app to have authentication capabilities for users. The primary reason for this is as follows: If I have multiple users on the application, I can improve the recommendation system from using content filtering to collaborative filtering. With collaborative filtering, recommendations not just depend on the information of each song, but also of what users who share your tastes like. The ultimate idea for this is to create a "Pool" type of feature, where song recommendations will be heavily influenced by the friends you choose to share a pool with, ultimately enabling much better recs. 

4. I'll need to take some of the pre-processing offline. Right now, it takes over a minute to get recommendations, between creating the features set for the user playlist and grabbing the mySQL database for comparison. A way to do this could potentially be creating another database for the just the features. That way the pipeline to the first database would contain all of the basic pre-processing, but then the second database could run and replace every time new songs are added with the one hot encoding and vectorizing, since this portion is where I would get an error if I  tried adding songs to the already existing database.
