import requests
import os
import base64
from urllib.request import urlopen
 
API_KEY = os.environ.get("LASTFM_API_KEY", "9f251154c3867781aab7e76e80a4f778")
USER = "gougy130"
 
def get_image_b64(url):
    try:
        with urlopen(url, timeout=5) as r:
            return base64.b64encode(r.read()).decode()
    except:
        return None
 
def get_tracks():
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={USER}&api_key={API_KEY}&format=json&limit=10"
    r = requests.get(url)
    data = r.json()
    tracks = data["recenttracks"]["track"]
    if not isinstance(tracks, list):
        tracks = [tracks]
 
    result = []
    seen = set()
    for t in tracks:
        np = t.get("@attr", {}).get("nowplaying") == "true"
        name = t.get("name", "")
        artist = t["artist"]["#text"]
        key = (name.lower(), artist.lower())
        if key in seen:
            continue
        seen.add(key)
        img_url = next((i["#text"] for i in t.get("image", []) if i["size"] == "medium"), "")
        default = "https://lastfm.freetls.fastly.net/i/u/64s/2a96cbd8b46e442fc41c2b86b821562f.png"
        img_b64 = get_image_b64(img_url) if img_url and img_url != default else None
        result.append({"name": name, "artist": artist, "img_b64": img_b64, "np": np})
        if len(result) == 5:
            break
    return result
 
def make_svg(tracks):
    rows = ""
    colors = ["#1a1a2e", "#16213e", "#0f3460", "#533483", "#2b2d42"]
    for i, t in enumerate(tracks):
        y = 20 + i * 56
 
        if t["img_b64"]:
            img_tag = f'<image href="data:image/jpeg;base64,{t["img_b64"]}" x="16" y="{y}" width="40" height="40" rx="4"/>'
        else:
            c = colors[i % len(colors)]
            img_tag = f'<rect x="16" y="{y}" width="40" height="40" rx="4" fill="{c}"/><text x="36" y="{y+25}" font-family="\'Segoe UI\',sans-serif" font-size="14" fill="#555" text-anchor="middle">{i+1}</text>'
 
        bars = ""
        if t["np"]:
            for bx, delay, h1, h2 in [(64,0,12,4),(69,0.15,4,10),(74,0.3,8,6)]:
                bars += f'<rect x="{bx}" y="{y+20}" width="3" height="12" rx="1" fill="#d51007"><animate attributeName="height" values="{h1};{h2};{h1}" dur="0.9s" begin="{delay}s" repeatCount="indefinite"/><animate attributeName="y" values="{y+20};{y+20+(h1-h2)//2};{y+20}" dur="0.9s" begin="{delay}s" repeatCount="indefinite"/></rect>'
 
        name = t["name"][:28] + ("…" if len(t["name"]) > 28 else "")
        artist = t["artist"][:32] + ("…" if len(t["artist"]) > 32 else "")
        tx = "84" if t["np"] else "68"
 
        rows += f"""<g>
          {img_tag}
          {bars}
          <text x="{tx}" y="{y+16}" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="500" fill="#e8e8e8">{name}</text>
          <text x="{tx}" y="{y+32}" font-family="'Segoe UI',sans-serif" font-size="11" fill="#888">{artist}</text>
          {"<text x='490' y='" + str(y+16) + "' font-family=\"'Segoe UI',sans-serif\" font-size='11' fill='#d51007' text-anchor='end'>now playing</text>" if t["np"] else ""}
        </g>"""
 
    height = 20 + len(tracks) * 56 + 20
    svg = f"""<svg width="500" height="{height}" viewBox="0 0 500 {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <rect width="500" height="{height}" rx="10" fill="#111"/>
  {rows}
</svg>"""
    return svg
 
tracks = get_tracks()
svg = make_svg(tracks)
with open("lastfm.svg", "w") as f:
    f.write(svg)
print("Generated lastfm.svg")
 