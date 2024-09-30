import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from dotenv import load_dotenv

app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/download": {"origins": "https://clarkson1415.github.io"}})

load_dotenv()  # Load variables from .env

# Your YouTube Data API key
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is not set.")


def get_video_metadata(video_id):
    url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet,contentDetails,statistics'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]  # Return the first video's metadata
        else:
            return None
    else:
        print(f"Error fetching metadata: {response.status_code} - {response.text}")
        return None

def sanitize_filename(filename):
    """Replace illegal characters in filename."""
    return filename.replace(':', '').replace('?', '').replace('/', '_').replace('\\', '_').replace(' ', '_')

def download_youtube(url, output_format):
    """Download YouTube video and return the file path."""
    output_path = os.path.join(os.path.expanduser('~'), 'YTtoMP3')
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best' if output_format == 'mp3' else 'bestvideo+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if output_format == 'mp3' else 'FFmpegVideoConvertor',
            'preferredcodec': 'mp3' if output_format == 'mp3' else 'mp4',
            'preferredquality': '192' if output_format == 'mp3' else None,
        }],
        'outtmpl': os.path.join(output_path, f"{sanitize_filename('%(title)s.%(ext)s')}"),
        'nocheckcertificate': True,  # Skip SSL certificate check
        'age_limit': 18,  # Attempt to bypass age restrictions
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            video_info = ydl.extract_info(url, download=False)
            expected_title = sanitize_filename(video_info['title'])
            expected_file_name = os.path.join(output_path, f"{expected_title}.{output_format}")
            return expected_file_name, None
        except Exception as e:
            return None, str(e)

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    elif "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return None

@app.route('/download', methods=['POST'])
def download():
    print("Received request to /download")  # Add logging
    try:
        data = request.json
        url = data.get('url')
        output_format = data.get('format')

        if not url or not output_format:
            return jsonify({"success": False, "error": "URL and format are required."}), 400

        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({"success": False, "error": "Invalid URL. Please provide a valid YouTube video URL."}), 400

        metadata = get_video_metadata(video_id)

        if not metadata:
            return jsonify({"success": False, "error": "Could not fetch video metadata."}), 404

        file_path, error = download_youtube(url, output_format)

        if error:
            return jsonify({"success": False, "error": error}), 500

        return jsonify({"success": True, "file_path": file_path}), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
