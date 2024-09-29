import os
import json
from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def sanitize_filename(filename):
    """Replace illegal characters in filename."""
    return filename.replace(':', '').replace('?', '').replace('/', '_').replace('\\', '_').replace(' ', '_')

def download_youtube(url, output_format):
    """Download YouTube video and return the file path."""
    output_path = os.path.join(os.path.expanduser('~'), 'YTtoMP3')

    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {}
    if output_format == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, f"{sanitize_filename('%(title)s.%(ext)s')}"),
        }
    elif output_format == 'mp4':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'outtmpl': os.path.join(output_path, f"{sanitize_filename('%(title)s.%(ext)s')}"),
        }
    else:
        return None, "Invalid format selected."

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            video_info = ydl.extract_info(url, download=False)
            expected_title = sanitize_filename(video_info['title'])
            expected_file_name = os.path.join(output_path, f"{expected_title}.{output_format}")
            return expected_file_name, None
        except Exception as e:
            return None, str(e)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    output_format = data.get('format')

    if not url or not output_format:
        return jsonify({"success": False, "error": "URL and format are required."}), 400

    file_path, error = download_youtube(url, output_format)

    if error:
        return jsonify({"success": False, "error": error}), 500

    return jsonify({"success": True, "file_path": file_path}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
