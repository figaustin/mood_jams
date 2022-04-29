import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models.mood import Mood
from flask_app.controllers.main import recommend, create_playlist
import random

@app.route('/mood/custom_maker')
def make_custom():

    directory = './flask_app/static/imgs'

    imgs = []

    for file in os.listdir(directory):
        f = os.path.join(directory, file)

        if os.path.isfile(f):
            imgs.append(file)

    return render_template('/custom_mood.html')

@app.route('/mood/custom', methods=["POST"])
def custom():

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    energy = int(request.form['energy']) / 100
    dance = int(request.form['dance']) / 100
    valence = int(request.form['valence']) / 100
    
    recs = []
    playlist = []

    tracks = spotify.recommendations(seed_genres=[request.form['genres']], target_energy=energy, target_danceability=dance, target_valence=valence, limit=100)

    for item in tracks['tracks']:
        if tracks['tracks'] not in recs:
            recs.append(random.choice(tracks['tracks']))

    for track in range(0,25):
        playlist.append(recs[track])

    new_playlist = spotify.user_playlist_create(spotify.me()['id'], "Mood Jams Custom", public=False,collaborative=False,description=f"Playlist created by Mood Jams for {spotify.me()['display_name']}")

    id = new_playlist['id']
    uris = []

    for uri in playlist:
        uris.append(uri['uri'])
    joined_uris = ','

    spotify.user_playlist_add_tracks(user=spotify.me(), playlist_id=id, tracks=uris, position=None)


    print(tracks)

    return go_to_playlist(id)

def go_to_playlist(playlist_id):
    return render_template('custom.html', playlist_id = playlist_id)


caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    print("Session folder made")
    os.makedirs(caches_folder)

def session_cache_path():
    print("Session cache path found")
    return caches_folder + session.get('uuid')