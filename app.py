from config import Config
from flask_cors import CORS, cross_origin
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__, static_folder='dist/', static_url_path='/')
app.config.from_object(Config)
# todo add these to config file
# stripe.api_key = 'sk_test_....' 
# endpoint_secret = 'whsec_...'

app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = Config.SECRET_KEY
# Create a SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
    f"?ssl_ca={Config.APP_PATH}/isrgrootx1.pem"
    )
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow any origin for development, specify http://beta.ufarms.co/ origins in production
db = SQLAlchemy(app)

# findme explore this
user_info = {}

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
        submission = Config.PreLaunch(zipcode=zipcode, email=email, interests=', '.join(produce_type))
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
    
# Stripe Integration
# findme todo

@app.route('/pay', methods=['POST'])
def pay():
    email = request.json.get('email', None)

    if not email:
        return 'You need to send an Email!', 400

    intent = stripe.PaymentIntent.create(
        amount=50000, # unit is in cents
        currency='usd',
        receipt_email=email
    )

    return {"client_secret": intent['client_secret']}, 200

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe_Signature', None)

    if not sig_header:
        return 'No Signature Header!', 400

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    if event['type'] == 'payment_intent.succeeded':
        email = event['data']['object']['receipt_email'] # contains the email that will recive the recipt for the payment (users email usually)
        
        user_info['paid_50'] = True
        user_info['email'] = email
    else:
        return 'Unexpected event type', 400

    return '', 200

@app.route('/user', methods=['GET'])
def user():
    return user_info, 200

#  END

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)