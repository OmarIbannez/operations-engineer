# You will need to pip install flask and the sqlalchemy extension for flask.
from flask import Flask

# Initialize the application.
app = Flask(__name__)
app.config.from_pyfile("config.py")

# Import the views file for routing.
import accounting.views
