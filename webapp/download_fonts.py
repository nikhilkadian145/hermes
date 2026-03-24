import os
import urllib.request
import re

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
url_sans = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap'
url_mono = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&display=swap'

os.makedirs('frontend/public/fonts', exist_ok=True)

final_css = ""

def download_and_process(url, prefix):
    global final_css
    req = urllib.request.Request(url, headers={'User-Agent': agent})
    with urllib.request.urlopen(req) as response:
        css = response.read().decode('utf-8')
    
    urls = re.findall(r'url\((https://[^)]+)\)', css)
    for i, w_url in enumerate(set(urls)):
        filename = f"{prefix}_{i}.woff2"
        filepath = os.path.join('frontend/public/fonts', filename)
        if not os.path.exists(filepath):
            urllib.request.urlretrieve(w_url, filepath)
        
        css = css.replace(w_url, f"/fonts/{filename}")
    
    final_css += css + "\n"

download_and_process(url_sans, "ibm_plex_sans")
download_and_process(url_mono, "ibm_plex_mono")

os.makedirs('frontend/src/styles', exist_ok=True)
with open('frontend/src/styles/fonts.css', 'w', encoding='utf-8') as f:
    f.write(final_css)

print("Fonts downloaded and fonts.css generated.")
