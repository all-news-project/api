import uuid

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid4())

from server_api import routes

try:
    from flask_cors import CORS, cross_origin
except ImportError:
    pass

CORS(app)
