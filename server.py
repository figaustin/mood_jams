from flask_app import app
from flask_app.controllers import main
from flask_app.controllers import custom_mood

if __name__ == '__main__':
    app.run(debug=True)