from config import Config
from flask_cors import CORS, cross_origin
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_folder='dist/', static_url_path='/')
app.config.from_object(Config)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = Config.SECRET_KEY
# Create a SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
    f"?ssl_ca={Config.APP_PATH}/isrgrootx1.pem"
    )
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow any origin for development, specify http://beta.ufarms.co/ origins in production
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

## Models
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.String(255))
    email = db.Column(db.String(255))
    interests = db.Column(db.String(255))


@app.route('/api/submit_form', methods=['POST'])
@cross_origin()
def submit_form():

    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')  # Modified line
        return response

    if request.method == 'POST':
        data = request.get_json()
        zipcode = data.get('zipcode')
        email = data.get('email')
        produce_type = data.get('produceType', [])
        print(email)
        submission = Submission(zipcode=zipcode, email=email, interests=', '.join(produce_type))
        print(produce_type)
        try:
            # Add the Submission object to the database session
            db.session.add(submission)
            # Commit the changes to the database
            db.session.commit()

            return jsonify({'status': 'success'})
        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            # Close the database session
            db.session.close()
    else:
        return jsonify({'status': 'error'})

# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
#     response.headers.add('Access-Control-Allow-Methods', 'POST')
#     return response
###

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)