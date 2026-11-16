import io, json, os, time, requests
from palette import get_palette

ALBUMS_PER_ARTIST = 15
SAVE_EVERY = 10  # artists

# Read artists (one per line), drop blanks and duplicates
artists = [l.strip() for l in open("artists.txt", encoding="utf-8") if l.strip()]
artists = list(dict.fromkeys(artists))

# Resume where we left off if a previous run was stopped
albums = json.load(open("albums.json")) if os.path.exists("albums.json") else {}
done = set(json.load(open("done.json"))) if os.path.exists("done.json") else set()


def save():
    json.dump(albums, open("albums.json", "w"))
    json.dump(sorted(done), open("done.json", "w"))


def get(url, **kw):
    for _ in range(3):  # retry a few times if the request fails
        try:
            r = requests.get(url, timeout=15, **kw)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(5)
    return None


for i, artist in enumerate(artists, 1):
    if artist in done:
        continue
    r = get("https://itunes.apple.com/search",
            params={"term": artist, "entity": "album",
                    "limit": ALBUMS_PER_ARTIST * 2})
    if r is None:
        print("Skipped (no response):", artist)
        continue
    for a in r.json()["results"]:
        key = str(a["collectionId"])
        if key in albums or artist.lower() not in a["artistName"].lower():
            continue
        name = a["collectionName"].lower()
        if name.endswith(" - single") or name.endswith(" - ep"):
            continue  # official albums only
        if a.get("trackCount", 99) < 7:
            continue
        cover = a["artworkUrl100"].replace("100x100bb", "300x300bb")
        img = get(cover)
        if img is None:
            continue
        colors, weights = get_palette(io.BytesIO(img.content))
        albums[key] = {
            "title": a["collectionName"],
            "artist": a["artistName"],
            "cover": cover,
            "link": a["collectionViewUrl"],
            "palette": colors,
            "weights": weights,
            "trackCount": a.get("trackCount", 0),
            "year": a.get("releaseDate", "")[:4],
            "genre": a.get("primaryGenreName", ""),
        }
    done.add(artist)
    print(f"{i}/{len(artists)}  {artist}  ({len(albums)} albums)")
    if len(done) % SAVE_EVERY == 0:
        save()
    time.sleep(3)

save()
print("Finished:", len(albums), "albums")
