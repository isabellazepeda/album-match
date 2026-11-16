import io, random, requests
from palette import get_palette
from matcher import albums, rank, base_title

# Self-test: feed 100 random album covers back in as if they were photos.
# A good matcher should return the same album at #1 almost every time.
random.seed(1)
sample = random.sample(albums, min(100, len(albums)))
top1 = top5 = 0
for a in sample:
    img = requests.get(a["cover"], timeout=15).content
    colors, weights = get_palette(io.BytesIO(img))
    found = [base_title(x) for _, x in rank(colors, weights, top=5)]
    top1 += found[0] == base_title(a)
    top5 += base_title(a) in found

n = len(sample)
print(f"Tested {n} covers: correct album at #1 {top1 / n:.0%}, in top 5 {top5 / n:.0%}")
