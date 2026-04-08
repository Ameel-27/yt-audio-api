from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app);

@app.route("/search")
def search():
    query = request.args.get("query")

    if not query:
        return jsonify({"error": "No query provided"})

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            video = info['entries'][0]

            return jsonify({
                "title": video.get("title"),
                "audio_url": video.get("url"),
                "thumbnail": video.get("thumbnail"),
                "duration": video.get("duration")
            })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)