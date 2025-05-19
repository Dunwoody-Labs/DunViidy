from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '../video_store/unproccessed_vids'
EMAIL_FOLDER = '../video_store/proccessed_vids'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        original_name = secure_filename(file.filename)
        name, _ = os.path.splitext(original_name)  # discard original extension
        base_filename = f"{name}.mp4"

        # Auto-rename if needed
        counter = 1
        final_filename = base_filename
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], final_filename)):
            final_filename = f"{name}({counter}).mp4"
            counter += 1

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
        file.save(filepath)

        # Return the actual saved filename to the frontend
        return final_filename, 200

    return 'No file uploaded', 400

@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.form.get('email')
    video_name = request.form.get('video_name')

    if not email or not video_name:
        return 'Missing email or video name', 400

    os.makedirs(EMAIL_FOLDER, exist_ok=True)

    # Remove .mp4 extension if present
    name, _ = os.path.splitext(video_name)
    safe_name = secure_filename(name)
    email_path = os.path.join(EMAIL_FOLDER, f'{safe_name}.txt')

    with open(email_path, 'w') as f:
        f.write(email + '\n')

    return 'Email recorded', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
