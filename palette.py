from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

def get_palette(path, n=5):
    img = Image.open(path).convert("RGB").resize((150, 150))
    pixels = np.array(img).reshape(-1, 3)
    km = KMeans(n_clusters=n, n_init=3).fit(pixels)
    weights = np.bincount(km.labels_, minlength=n) / len(pixels)
    return km.cluster_centers_.astype(int).tolist(), weights.round(3).tolist()
