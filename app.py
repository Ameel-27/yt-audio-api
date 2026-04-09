from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import time
import os

app = Flask(__name__)
CORS(app)

# Cache setup
cache = {}
CACHE_TTL = 600  # seconds

def fetch_video(query, retries=3):
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--dump-json",
        "-f", "bestaudio/best",
        "--no-warnings",
        "--quiet"
    ]

    for attempt in range(retries):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=20
            )

            if result.returncode != 0:
                raise Exception(result.stderr.strip())

            # Parse first line of JSON output
            data = json.loads(result.stdout.splitlines()[0])

            # Extract best audio URL
            formats = data.get("formats", [])
            audio_url = next(
                (f["url"] for f in formats if f.get("acodec") != "none"),
                data.get("url")
            )

            return {
                "title": data.get("title"),
                "audio_url": audio_url,
                "thumbnail": data.get("thumbnail"),
                "duration": data.get("duration")
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt) 

@app.route("/search")
def search():
    query = request.args.get("query", "").strip().lower()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Check cache
    if query in cache:
        cached_result, timestamp = cache[query]
        if (time.time() - timestamp) < CACHE_TTL:
            return jsonify(cached_result)
        del cache[query]

    try:
        result = fetch_video(query)
        cache[query] = (result, time.time())
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)