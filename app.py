"""
Production server entry point
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from src.config import get_config
from src.database import init_db
from src.api import api

config = get_config()

app = Flask(__name__, static_folder='frontend')
app.config["SECRET_KEY"] = config.SECRET_KEY
CORS(app)

# Register API
app.register_blueprint(api)

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

# Init database
with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
