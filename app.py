from flask import Flask, render_template,jsonify,send_from_directory,abort,request
from supabase import create_client, Client

supabase_url="https://pnimkcozraghtqqxynly.supabase.co"
anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaW1rY296cmFnaHRxcXh5bmx5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNDUxODUwOCwiZXhwIjoyMDQwMDk0NTA4fQ.h1tA9BepiInamSfxw6JioHpdYTXRgk_Wnbcm69UefqY"
app = Flask(__name__)

supabase: Client = create_client(supabase_url, anon_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check')
def chk():
    return "maro rohit ki"

@app.route('/upload')
def upload():
    return render_template('upload.html')
@app.route('/test-connection')
def test_connection():
    try:
        response = supabase.table("SongsTable").select("*").execute()
        data = response.data
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list-buckets')
def list_buckets():
    try:
        # List all buckets
        buckets = supabase.storage.list_buckets()
        # Return the bucket names
        return jsonify(buckets), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/refresh')
def insert_or_update_song_metadata():
    # Define the bucket name
    bucket_name = 'Songs'
    
    try:
        # Access the bucket
        bucket = supabase.storage.get_bucket(bucket_name)
        
        # List files in the bucket
        files = bucket.list()
        
        
        # files = files_response.data
        
        # Iterate through files and insert/update metadata
        print(files)
        for file in files:
            file_name = file['name']
            
            # Extract metadata from file name or use placeholder values
            title = file_name.split('.')[0]  # Placeholder for title
            artist = 'Unknown'  # Placeholder for artist
            print(title)

            file_url = bucket.get_public_url(file['name'])
            # Check if song already exists in the database
            response = supabase.table('SongsTable').select('*').eq('url', file_url).execute()
            
            # # Check for errors in the response
            # if response.error:
            #     return jsonify({'error': response.error}), 500
            
            response_data = response.data
            
            if response_data:
                # Update existing record
                song_id = response_data[0]['id']
                update_response = supabase.table('SongsTable').update({
                    'title': title,
                    'artist': artist
                }).eq('id', song_id).execute()
            else:
                # Insert new record
                insert_response = supabase.table('SongsTable').insert({
                    'title': title,
                    'artist': artist,
                    'url': file_url
                }).execute()
                
                # Check for errors in insert response
                # if insert_response.error:
                #     return jsonify({'error': insert_response.error}), 500
        return jsonify({"message": "Metadata updated successfully!"}), 200

    except Exception as e:
        # logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


    
@app.route('/songs')
def songs_list():
    try:
        # Fetch songs data from Supabase
        response = supabase.table('SongsTable').select('title, artist, url').execute()
        
        # Check for errors in the response
        if not response:
            return jsonify({'error'}), 500
        
        songs = response.data
        # Render the template with the song data
        return render_template('list_songs.html', songs=songs)
    
    except Exception as e:
        # logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/songs/<int:id>', methods=['GET'])
def get_song(id):
    response = supabase.table('SongsTable').select('*').eq('id', id).execute()
    # return jsonify(response.data)
    if response and response.data:
        return jsonify(response.data[0]['url']), 200
    else:
        return jsonify({'error': 'Song not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)