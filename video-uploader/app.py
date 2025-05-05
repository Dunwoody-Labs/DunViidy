from flask import Flask, render_template, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No video file provided", 400
    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return f"Uploaded: {file.filename}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
