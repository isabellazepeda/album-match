import json, re, sys
import numpy as np
from palette import get_palette

# Tuning dials: change these and rerun to see how results shift
NEUTRAL_FLOOR = 0.25   # weight kept by gray/black/white colors (0 = ignore them)
CHROMA_SCALE = 60      # how fast saturated colors gain importance
BRIGHTNESS_PENALTY = 0.15  # penalty per point of overall brightness gap


def to_lab(palette):
    """sRGB (0-255) -> CIE Lab, so distances match how colors look."""
    c = np.array(palette, dtype=float).reshape(-1, 3) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.412453, 0.357580, 0.180423],
                        [0.212671, 0.715160, 0.072169],
                        [0.019334, 0.119193, 0.950227]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.column_stack([116 * f[:, 1] - 16,
                            500 * (f[:, 0] - f[:, 1]),
                            200 * (f[:, 1] - f[:, 2])])


def salience(lab, w):
    """Area x saturation: bold colors matter more than dull ones."""
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    s = w * (NEUTRAL_FLOOR + chroma / CHROMA_SCALE)
    return s / s.sum()


def prepare(colors, weights):
    lab, w = to_lab(colors), np.array(weights)
    return {"lab": lab, "s": salience(lab, w), "L": float(lab[:, 0] @ w)}


# Prepare every album once, when the program starts
MIN_TRACKS = 8
NOT_ALBUM = re.compile(
    r"greatest hits|best of|\bhits\b|collection|anthology|essential|"
    r"remix|karaoke|tribute|demos?\b|b-sides|rarities|2 in 1|compilation|"
    r"\(live|\[live|\blive (at|in|from|on)\b|unplugged", re.I)


def is_album(a):
    t = a["title"].lower()
    if t.endswith(" - single") or t.endswith(" - ep"):
        return False
    if a.get("trackCount", 99) < MIN_TRACKS:  # old entries without it pass
        return False
    return not NOT_ALBUM.search(t)


def base_title(a):
    t = re.sub(r"[\(\[].*?[\)\]]", "", a["title"].lower()).strip()
    return (a["artist"].lower(), t)


albums = [a for a in json.load(open("albums.json")).values() if is_album(a)]
for a in albums:
    a.update(prepare(a["palette"], a["weights"]))


def distance(p, a):
    d = np.linalg.norm(p["lab"][:, None] - a["lab"][None, :], axis=2)
    color_gap = (d.min(axis=1) @ p["s"] + d.min(axis=0) @ a["s"]) / 2
    return color_gap + BRIGHTNESS_PENALTY * abs(p["L"] - a["L"])


def match(photo_path, top=5):
    return rank(*get_palette(photo_path), top=top)


def rank(colors, weights, top=5):
    photo = prepare(colors, weights)
    scored = [(distance(photo, a), a) for a in albums]
    scored.sort(key=lambda x: x[0])
    results, seen = [], set()
    for score, a in scored:  # skip deluxe/remaster repeats of the same album
        if base_title(a) not in seen:
            seen.add(base_title(a))
            results.append((score, a))
        if len(results) == top:
            break
    return results


if __name__ == "__main__":
    for score, a in match(sys.argv[1]):
        print(f"{score:5.1f}  {a['artist']} - {a['title']}")
