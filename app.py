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

# pseudo-code mock-up findme
@app.route('api/submit_form', methods=['POST'])
def submit_form():
    
    if request.method == 'POST':
        zipcode = request.form.get('zipcode')
        email = request.form.get('email')
        produce_type = request.form.getlist('produceType')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (zipcode, email, produce_type)
            VALUES (?, ?, ?)
        ''', (zipcode, email, ', '.join(produce_type)))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)