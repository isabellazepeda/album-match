import csv, glob, sys
from collections import Counter

# Usage:
#   python add_artists.py playlists            (a folder full of CSVs)
#   python add_artists.py liked.csv cumbia.csv (specific files)
# Options: --min 2   only add artists with at least 2 songs across all files
#          --top 300 only add the 300 most-played new artists
args = sys.argv[1:]
opts = {"--min": 1, "--top": None}
for flag in opts:
    if flag in args:
        i = args.index(flag)
        opts[flag] = int(args[i + 1])
        del args[i:i + 2]

files = []
for p in args:
    files += glob.glob(p + "/*.csv") if "." not in p.split("\\")[-1] else [p]

counts = Counter()
for path in files:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    if not rows:
        continue
    col = next(c for c in rows[0] if "artist" in c.lower())  # "Artist Name(s)"
    for r in rows:
        for name in r[col].split(";"):  # Exportify separates artists with ";"
            if name.strip():
                counts[name.strip()] += 1

existing = {l.strip().lower() for l in open("artists.txt", encoding="utf-8")}
new = [a for a, n in counts.most_common(opts["--top"])
       if n >= opts["--min"] and a.lower() not in existing]

with open("artists.txt", "a", encoding="utf-8") as f:
    f.write("\n" + "\n".join(new) + "\n")

print(f"Read {len(files)} files, {len(counts)} unique artists, "
      f"added {len(new)} that weren't already in artists.txt")
