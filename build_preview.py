#!/usr/bin/env python
"""Build a single self-contained preview HTML with CSS, JS, font and images
all inlined as data URIs. Output: preview-nkosi-thatchers.html
Run:  py build_preview.py
"""
import base64, re, os

def datauri(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())

html = open("index.html", encoding="utf-8").read()
css  = open("css/styles.css", encoding="utf-8").read()
js   = open("js/main.js", encoding="utf-8").read()

# --- inline font into the CSS @font-face ---
font_uri = datauri("fonts/bitter-700.woff2", "font/woff2")
css = css.replace('url("../fonts/bitter-700.woff2") format("woff2")',
                  'url(%s) format("woff2")' % font_uri)

# --- one image per slug (800w webp where available, else the largest) ---
slugs = {
    "hero-house-pool": 800, "team": 800, "lapa-after": 800, "gazebo-after": 800,
    "lapa-before": 800, "braai-before": 800, "house-dawn": 800,
    "large-lapa": 800, "rondavel-dusk": 800, "rounded-lapa": 800,
    "house-palm": 800, "house-pool-2": 800, "house-yellow": 800,
    "chimney-detail": 715, "house-grand": 600,
}
img_uri = {s: datauri("images/%s-%d.webp" % (s, w), "image/webp") for s, w in slugs.items()}

# collapse responsive markup: drop <source>, srcset, sizes; keep a single src
html = re.sub(r"\s*<source[^>]*>", "", html)
html = re.sub(r'\s+srcset="[^"]*"', "", html)
html = re.sub(r'\s+sizes="[^"]*"', "", html)

# dedupe: neutralise the gallery link href + data-full so the big base64 blob
# is embedded ONCE (as the <img src>). The lightbox falls back to the img src.
html = re.sub(r'data-full="images/[^"]*"', 'data-full="#"', html)
html = re.sub(r'(<a class="gallery-item[^"]*") href="images/[^"]*"', r'\1 href="#gallery"', html)

# point every remaining images/<slug>-<w>.<ext> (the <img src>) at the data URI
for slug, uri in img_uri.items():
    html = re.sub(r"images/%s-\d+\.(?:webp|jpg)" % re.escape(slug), uri, html)

# inline favicon.svg; drop external icon/preload/og refs that can't resolve offline
fav = datauri("favicon.svg", "image/svg+xml")
html = html.replace('href="favicon.svg"', 'href="%s"' % fav)
html = re.sub(r'\s*<link rel="preload"[^>]*>', "", html)
html = re.sub(r'\s*<link rel="icon" href="favicon\.ico"[^>]*>', "", html)
html = re.sub(r'\s*<link rel="apple-touch-icon"[^>]*>', "", html)

# swap external stylesheet + script for inline versions
html = html.replace('<link rel="stylesheet" href="css/styles.css">',
                    "<style>\n%s\n</style>" % css)
html = html.replace('<script src="js/main.js" defer></script>',
                    "<script>\n%s\n</script>" % js)

out = "preview-nkosi-thatchers.html"
open(out, "w", encoding="utf-8").write(html)
print("wrote %s  (%.2f MB)" % (out, os.path.getsize(out) / 1048576))
