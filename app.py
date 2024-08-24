from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.api
import cloudinary.uploader

# Initialize Flask application
app = Flask(__name__)

# Configure the database (using PostgreSQL as an example)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure Cloudinary
cloudinary.config(
    cloud_name='dimdoq0ng',
    api_key='324659127373814',
    api_secret='eUTC_Jxfvw95dkaCDN7yHEomugE'
)

# Define the Song model
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'

# Create the database tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/up')
def up():
    return render_template("upload.html")

@app.route('/refresh', methods=['GET'])
def refresh_songs():
    try:
        # List all files in Cloudinary
        resources = cloudinary.api.resources(resource_type="video")['resources']
        
        # Get the URLs of the files already in the database
        existing_urls = {song.url for song in Song.query.all()}
        
        # Iterate through Cloudinary resources and add new ones to the database
        new_songs = []
        for resource in resources:
            file_url = resource['url']
            file_name = resource['public_id'].split('/')[-1]  # Extract filename from public_id
            
            if file_url not in existing_urls:
                new_song = Song(title=file_name, artist='NA', url=file_url)
                db.session.add(new_song)
                new_songs.append(new_song)
        
        db.session.commit()

        return jsonify({'message': f'{len(new_songs)} new songs added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_song():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    title = request.form.get('title')
    artist = request.form.get('artist')

    if not title or not artist:
        return jsonify({'error': 'Title and artist are required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Upload the song file to Cloudinary
    result = cloudinary.uploader.upload(file, resource_type="video")
    file_url = result['url']

    # Store the metadata in the database
    new_song = Song(title=title, artist=artist, url=file_url)
    db.session.add(new_song)
    db.session.commit()

    return jsonify({'message': 'Song uploaded successfully!', 'url': file_url}), 201


@app.route('/songs_list', methods=['GET'])
def list_songs():
    songs = Song.query.all()
    songs_data = [{'title': song.title, 'artist': song.artist, 'url': song.url} for song in songs]
    return render_template("list_songs.html",songs=songs_data)

@app.route('/songs/<int:id>', methods=['GET'])
def get_song(id):
    song = Song.query.get_or_404(id)
    return jsonify({
        'title': song.title,
        'artist': song.artist,
        'url': song.url
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
