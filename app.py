from flask import Flask, render_template,jsonify,send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check')
def chk():
    return "maro rohit ki"

# Directory where your music files are stored
MUSIC_DIR = os.path.join(app.root_path, 'static/songs')

# Endpoint to list all available songs
@app.route('/songs', methods=['GET'])
def list_songs():
    try:
        # List all the files in the music directory
        songs = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f))]
        return jsonify(songs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to serve a specific song file
@app.route('/songs/<filename>', methods=['GET'])
def serve_song(filename):
    try:
        return send_from_directory(MUSIC_DIR, filename)
    except FileNotFoundError:
        abort(404, description="Song not found")


if __name__ == '__main__':
    app.run(debug=True)