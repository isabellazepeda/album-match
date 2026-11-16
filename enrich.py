import json, time, requests

# One-time repair: add track counts, year and genre to albums already in
# albums.json, so singles / short releases can be filtered out.
albums = json.load(open("albums.json"))
need = [k for k, v in albums.items() if "trackCount" not in v]
print(len(need), "albums to update")

for i in range(0, len(need), 100):
    chunk = need[i:i + 100]
    found = set()
    try:
        r = requests.get("https://itunes.apple.com/lookup",
                         params={"id": ",".join(chunk)}, timeout=30)
        for a in r.json().get("results", []):
            k = str(a.get("collectionId"))
            if k in albums:
                albums[k]["trackCount"] = a.get("trackCount", 0)
                albums[k]["year"] = a.get("releaseDate", "")[:4]
                albums[k]["genre"] = a.get("primaryGenreName", "")
                found.add(k)
    except (requests.RequestException, ValueError):
        print("Request failed, rerun to retry the rest")
        break
    for k in chunk:  # no longer in the store: hide it
        if k not in found:
            albums[k]["trackCount"] = 0
    json.dump(albums, open("albums.json", "w"))
    print(f"{min(i + 100, len(need))}/{len(need)}")
    time.sleep(3)

print("Done")
