# Album Match

Upload any photo and get the 5 album covers whose colors match it best,
with links to find each album on Spotify and Apple Music.

**Live demo:** [https://album-match-5q5v.onrender.com/]

![screenshot](screenshot.png)

## How it works

1. **Palette extraction:** k-means clustering finds the 5 dominant colors in
   the photo, plus how much of the image each one covers.
2. **Perceptual color space:** colors are converted from RGB to CIE Lab, so
   distances match how different two colors actually look.
3. **Matching:** each color is weighted by its area *and* saturation (so a
   small vivid red outweighs a large patch of white), and the photo's palette
   is compared with every album's palette in both directions. A brightness
   penalty keeps very dark covers from matching bright photos.
4. **Album filtering:** singles, EPs, short releases, compilations, live
   albums and duplicate editions are removed so only real albums are returned.

## Data

About [N] albums from [N] artists, collected with Apple's iTunes Search API.
Only each cover's color palette and link are stored, not the images.

## Results

- Self-test: feeding 100 album covers back in returns the same album at #1
  [95]% of the time ([97]% in the top 5) (`python selftest.py`).
- Tuned the saliency weighting and brightness penalty after testing
  [100] photos against hand-picked "ideal" covers.

## Privacy

Uploaded photos are processed in memory and never saved.

## Run it yourself

```
pip3 install -r requirements.txt
python3 build_dataset.py   # builds albums.json (takes a while)
python3 app.py             # then open http://127.0.0.1:5001
```

Built with Python, Flask, scikit-learn, NumPy and Pillow.

## Ideas for next

- Match by genre or mood as well as color
- Use MusicBrainz to identify true studio albums
- Letterboxd-style ratings for albums
