from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__)
CORS(app);

cache = {}
CACHE_TTL = 600

def fetch_video(query, ydl_opts, retries=3, max_results=1):
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    ydl = yt_dlp.YoutubeDL(ydl_opts)

    for attempt in range(retries):
        try:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            entries = info.get('entries', [])

            if not entries:
                raise ValueError(f"No results found for query: {query}")
            return entries[0]
        
        except Exception as e:
            print(f"Attempt: {attempt + 1} failed: {e}")

            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)

@app.route("/search")
def search():
    query = request.args.get("query", "").strip().lower()

    if not query:
        return jsonify({"error": "No query provided"})
    
    if query in cache:
        cached_result, timestamp = cache[query]
        if (time.time() - timestamp) < CACHE_TTL:
            return jsonify(cached_result)
        del cache[query]

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            video = info['entries'][0]

            result = {
                "title": video.get("title"),
                "audio_url": video.get("url"),
                "thumbnail": video.get("thumbnail"),
                "duration": video.get("duration")
            }
            cache[query] = (result, time.time())

            return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)