import base64, io
from urllib.parse import quote
from flask import Flask, request, render_template_string
from palette import get_palette
from matcher import rank

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024  # 15 MB uploads

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Album Match</title>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; background: #121212;
         color: #f2f2f2; }
  main { max-width: 760px; margin: 0 auto; padding: 24px 16px 60px; }
  h1 { font-size: 28px; margin-bottom: 4px; }
  p.sub { color: #a8a8a8; margin-top: 0; }
  form { background: #1e1e1e; padding: 18px; border-radius: 14px; }
  input[type=file] { color: #ccc; width: 100%; margin-bottom: 14px; }
  button { background: #1db954; color: #000; border: 0; padding: 12px 22px;
           border-radius: 999px; font-weight: 700; font-size: 16px;
           cursor: pointer; }
  .photo { width: 100%; max-height: 380px; object-fit: contain;
           border-radius: 12px; margin: 22px 0 10px; background: #000; }
  .swatches { display: flex; height: 34px; border-radius: 8px;
              overflow: hidden; margin-bottom: 26px; }
  .swatches div { height: 100%; }
  .card { display: flex; gap: 16px; background: #1e1e1e; border-radius: 14px;
          padding: 14px; margin-bottom: 14px; align-items: center; }
  .card img { width: 110px; height: 110px; border-radius: 8px;
              object-fit: cover; flex-shrink: 0; }
  .rank { color: #1db954; font-weight: 700; font-size: 13px; }
  .title { font-size: 18px; font-weight: 700; margin: 2px 0; }
  .artist { color: #a8a8a8; margin-bottom: 10px; }
  .links a { display: inline-block; margin: 0 8px 6px 0; padding: 6px 12px;
             border-radius: 999px; border: 1px solid #555; color: #f2f2f2;
             text-decoration: none; font-size: 14px; }
  .links a:hover { border-color: #1db954; color: #1db954; }
  .error { color: #ff7b7b; margin-top: 14px; }
</style>
</head>
<body>
<main>
  <h1>Album Match</h1>
  <p class="sub">Upload a photo and find the album covers with the same colors.</p>

  <form method="post" enctype="multipart/form-data">
    <input type="file" name="photo" accept="image/*" required>
    <button type="submit">Find my albums</button>
  </form>

  {% if error %}<p class="error">{{ error }}</p>{% endif %}

  {% if results %}
    <img class="photo" src="data:image/jpeg;base64,{{ preview }}" alt="Your photo">
    <div class="swatches">
      {% for c, w in swatches %}
        <div style="background: rgb({{ c[0] }},{{ c[1] }},{{ c[2] }}); flex: {{ w }}"></div>
      {% endfor %}
    </div>

    {% for r in results %}
      <div class="card">
        <img src="{{ r.cover }}" alt="Cover of {{ r.title }}">
        <div>
          <div class="rank">#{{ loop.index }} MATCH</div>
          <div class="title">{{ r.title }}</div>
          <div class="artist">{{ r.artist }}{% if r.year %} &middot; {{ r.year }}{% endif %}</div>
          <div class="links">
            <a href="{{ r.spotify }}" target="_blank" rel="noopener">Find on Spotify</a>
            <a href="{{ r.link }}" target="_blank" rel="noopener">Apple Music</a>
          </div>
        </div>
      </div>
    {% endfor %}
  {% endif %}
</main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(PAGE)

    data = request.files["photo"].read()
    try:
        colors, weights = get_palette(io.BytesIO(data))
    except Exception:
        return render_template_string(
            PAGE, error="Sorry, I couldn't read that image. Try a JPG or PNG.")

    results = []
    for _, a in rank(colors, weights, top=5):
        results.append({
            "title": a["title"], "artist": a["artist"], "cover": a["cover"],
            "year": a.get("year", ""), "link": a["link"],
            "spotify": "https://open.spotify.com/search/"
                       + quote(f'{a["artist"]} {a["title"]}'),
        })

    preview = base64.b64encode(data).decode()
    return render_template_string(
        PAGE, results=results, preview=preview,
        swatches=list(zip(colors, weights)))


if __name__ == "__main__":
    app.run(port=5001)
