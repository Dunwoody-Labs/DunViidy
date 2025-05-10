from flask import Flask, render_template, request
import os
from datetime import datetime  # <-- missing import

UPLOAD_FOLDER = '../video_store/proccessed_vids'
EMAIL_FOLDER = '../video_store/unproccessed_vids'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return '', 204
    return 'No file uploaded', 400

@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.form.get('email')

    if not email:
        return 'Missing email', 400

    os.makedirs(EMAIL_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}.txt'

    with open(os.path.join(EMAIL_FOLDER, filename), 'w') as f:
        f.write(email + '\n')

    return 'Email saved', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
