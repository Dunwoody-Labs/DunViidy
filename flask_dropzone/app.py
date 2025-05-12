from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime 

UPLOAD_FOLDER = '../video_store/proccessed_vids'
EMAIL_FOLDER = '../video_store/unproccessed_vids'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')  # Get the uploaded file
    if file:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)  # Save the uploaded file
        return jsonify({"filename": file.filename}), 200  # Return the filename as JSON
    return 'No file uploaded', 400

@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.form.get('email')  # Get the email from the form
    video_name = request.form.get('video_name')  # Get the video name from the form

    if not email:
        return 'Missing email', 400

    if not video_name:
        return 'Missing video name', 400

    os.makedirs(EMAIL_FOLDER, exist_ok=True)  # Ensure the email folder exists
    filename = f'{os.path.splitext(video_name)[0]}.txt'  # Use the video name for the text file
    file_path = os.path.join(EMAIL_FOLDER, filename)

    with open(file_path, 'w') as f:
        f.write(email + '\n')  # Write the email to the file

    return 'Email saved', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)