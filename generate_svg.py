import requests
import os

API_KEY = os.environ.get("LASTFM_API_KEY", "9f251154c3867781aab7e76e80a4f778")
USER = "gougy130"

def get_tracks():
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={USER}&api_key={API_KEY}&format=json&limit=5"
    r = requests.get(url)
    data = r.json()
    tracks = data["recenttracks"]["track"]
    if not isinstance(tracks, list):
        tracks = [tracks]
    result = []
    for t in tracks:
        np = t.get("@attr", {}).get("nowplaying") == "true"
        name = t.get("name", "")
        artist = t["artist"]["#text"]
        img = next((i["#text"] for i in t.get("image", []) if i["size"] == "medium"), "")
        result.append({"name": name, "artist": artist, "img": img, "np": np})
    return result

def make_svg(tracks):
    rows = ""
    for i, t in enumerate(tracks):
        y = 20 + i * 56
        img_tag = f'<image href="{t["img"]}" x="16" y="{y}" width="40" height="40" rx="4" clip-path="url(#round)"/>' if t["img"] else ""
        dot = '<circle cx="64" cy="' + str(y+8) + '" r="4" fill="#d51007"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/></circle>' if t["np"] else ""
        bars = ""
        if t["np"]:
            for b, (bx, delay, h1, h2) in enumerate([(64,0,12,4),(69,0.15,4,10),(74,0.3,8,6)]):
                bars += f'<rect x="{bx}" y="{y+20}" width="3" height="12" rx="1" fill="#d51007"><animate attributeName="height" values="{h1};{h2};{h1}" dur="0.9s" begin="{delay}s" repeatCount="indefinite"/><animate attributeName="y" values="{y+20};{y+20+(h1-h2)//2};{y+20}" dur="0.9s" begin="{delay}s" repeatCount="indefinite"/></rect>'

        name = t["name"][:28] + ("…" if len(t["name"]) > 28 else "")
        artist = t["artist"][:32] + ("…" if len(t["artist"]) > 32 else "")

        rows += f"""
        <g>
          {img_tag}
          {bars if t["np"] else ""}
          <text x="{"84" if t["np"] else "68"}" y="{y+16}" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="500" fill="#e8e8e8">{name}</text>
          <text x="{"84" if t["np"] else "68"}" y="{y+32}" font-family="'Segoe UI',sans-serif" font-size="11" fill="#888">{artist}</text>
          <text x="480" y="{y+16}" font-family="'Segoe UI',sans-serif" font-size="11" fill="#555" text-anchor="end">{"now playing" if t["np"] else str(i+1)}</text>
        </g>
        """

    height = 20 + len(tracks) * 56 + 20
    svg = f"""<svg width="500" height="{height}" viewBox="0 0 500 {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <clipPath id="round"><rect width="40" height="40" rx="4"/></clipPath>
  </defs>
  <rect width="500" height="{height}" rx="10" fill="#111"/>
  {rows}
</svg>"""
    return svg

tracks = get_tracks()
svg = make_svg(tracks)
with open("lastfm.svg", "w") as f:
    f.write(svg)
print("Generated lastfm.svg")
