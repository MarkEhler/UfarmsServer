from config import Config
from flask_cors import CORS, cross_origin
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__, static_folder='dist/', static_url_path='/')
app.config.from_object(Config)
app.config['CORS_HEADERS'] = 'Content-Type'
# app.secret_key = Config.SECRET_KEY
# Create a SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
    f"?ssl_ca={Config.APP_PATH}/isrgrootx1.pem"
    )
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow any origin for development, specify actual origins in production
db = SQLAlchemy(app)

## Routes

# API route
@app.route('/api/time')
@cross_origin()
def get_current_time():
    return {'time': time.time()}

# React app route
@app.route('/')
def index():
    try:
        # Try to serve the React app's index.html
        return app.send_static_file('index.html')
    except:
        return send_from_directory('dist/', '404.html')

# pseudo-code mock-up findme
@app.route('/api/submit_form', methods=['POST'])
@cross_origin()
def submit_form():
    
    if request.method == 'POST':
        zipcode = request.form.get('zipcode')
        email = request.form.get('email')
        produce_type = request.form.getlist('produceType')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (zipcode, email, Interests)
            VALUES (?, ?, ?)
        ''', (zipcode, email, ', '.join(produce_type)))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'})

###

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)