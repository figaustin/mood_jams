import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models.mood import Mood
import random
import uuid


######################################################
############## AUTH/USER LOGIN ######################
####################################################
caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    print("Session folder made")
    os.makedirs(caches_folder)

def session_cache_path():
    print("Session cache path found")
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
        print("uuid given")

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing user-modify-playback-state user-read-playback-state playlist-modify-public playlist-modify-private',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)


    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('index.html', auth_url = auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/moods')

@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/moods')
def moods():

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    moods = Mood.get_all_moods()

    user = spotify.me()['display_name']
    
    return render_template('moods.html', moods = moods, user = user)


@app.route('/mood/<int:mood_id>')
def get_mood(mood_id):

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    


    picked_mood = {
        'mood_id' : mood_id
    }

    use_mood = Mood.get_mood_by_id(picked_mood)

    mood = use_mood

    tracks = recommend(use_mood)
    print(type(tracks))

    playlist = create_playlist(tracks, mood)
    playlist_id = playlist['id']
    

    return render_template('playlist.html', mood = mood, tracks = tracks, playlist_id = playlist_id)


@app.route('/mood/creator')
def creator():

    directory = './flask_app/static/imgs'

    imgs = []

    for file in os.listdir(directory):
        f = os.path.join(directory, file)

        if os.path.isfile(f):
            imgs.append(file)
    
    print(imgs)
    return render_template('new_mood.html', imgs = imgs)

@app.route('/mood/new', methods=["POST"])
def new_mood():

    energy = int(request.form['energy']) / 100
    dance = int(request.form['dance']) / 100
    valence = int(request.form['valence']) / 100

    print(request.form["bg_img"])
    
    query_data = {
        'name' : request.form['name'],
        'energy' : energy,
        'dance' : dance,
        'valence' : valence,
        'bg_img' : request.form['bg_img'],
        'genres' : request.form['genres'],

    }

    Mood.create_mood(query_data)

    return redirect('/moods')

@app.route('/mood/<int:mood_id>/delete')
def delete_mood(mood_id):
    
    query_data = {
        'mood_id' : mood_id
    }

    Mood.delete_mood(query_data)

    return redirect('/moods')

@app.route('/moods/edit')
def start_edit():
    moods = Mood.get_all_moods()
    return render_template('/startedit.html', moods = moods)

@app.route('/mood/<int:mood_id>/edit')
def edit_moood(mood_id):

    directory = './flask_app/static/imgs'

    imgs = []

    for file in os.listdir(directory):
        f = os.path.join(directory, file)

        if os.path.isfile(f):
            imgs.append(file)

    query_data = {
        'mood_id' : mood_id,
    }

    mood = Mood.get_mood_by_id(query_data)

    return render_template('/editmood.html', mood = mood, imgs = imgs)

@app.route('/mood/<int:mood_id>/update', methods=["POST"])
def update_mood(mood_id):

    energy = int(request.form['energy']) / 100
    dance = int(request.form['dance']) / 100
    valence = int(request.form['valence']) / 100

    updated_info = {
        'mood_id' : mood_id,
        'name' : request.form['name'],
        'energy' : energy,
        'dance' : dance,
        'valence' :valence,
        'bg_img' : request.form['bg_img'],
        'genres' : request.form['genres'],
    }

    Mood.update_mood(updated_info)
    return redirect('/moods')


def recommend(mood):

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    

    recs = []
    playlist = []

    tracks = spotify.recommendations(seed_genres=[mood.genres], target_energy=mood.energy, target_danceability=mood.dance, target_valence=mood.valence, limit=100)

    for item in tracks['tracks']:
        if tracks['tracks'] not in recs:
            recs.append(random.choice(tracks['tracks']))

    for track in range(0,25):
        playlist.append(recs[track])

    
    return playlist

def create_playlist(tracks, mood):

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    new_playlist = spotify.user_playlist_create(spotify.me()['id'], "Mood Jams " + mood.name, public=False,collaborative=False,description=f"Playlist created by Mood Jams for {spotify.me()['display_name']}")

    id = new_playlist['id']
    uris = []

    for uri in tracks:
        uris.append(uri['uri'])
    joined_uris = ','

    spotify.user_playlist_add_tracks(user=spotify.me(), playlist_id=id, tracks=uris, position=None)
    print(joined_uris.join(uris))

    return new_playlist
 


