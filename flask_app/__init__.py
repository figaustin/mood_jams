import os
from flask import Flask, session, request, redirect

app = Flask(__name__)
app.secret_key = 'spotkjnlkfjn3ljinapoiufn3242fa32'


if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))