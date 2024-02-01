from flask_cors import CORS
import time
from flask import Flask
from flask import Flask, jsonify, request


app = Flask(__name__, static_folder='react-deploy/build', static_url_path='/')
CORS(app)


# API route
@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

# React app route
@app.route('/')
def index():
    try:
        # Try to serve the React app's index.html
        return app.send_static_file('index.html')
    except:
        # If an exception occurs (e.g., connection error or file not found), serve a fallback landing page
        return send_from_directory('react-flask-deploy/build', '404.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)