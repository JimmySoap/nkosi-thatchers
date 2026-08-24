#!/usr/bin/env python
"""Build a self-hosted WordPress theme (.zip) from the static site.

Converts index.html into a WP theme: rewrites asset paths to
get_template_directory_uri(), enqueues CSS/JS via functions.php, adds
wp_head()/wp_footer(), bundles the font + web images + favicons.

Run:  py build_wp_theme.py
Output: wp-theme/nkosi-thatchers/  and  nkosi-thatchers-theme.zip
Upload the .zip in WordPress: Appearance > Themes > Add New > Upload Theme.
"""
import os, re, shutil, glob, zipfile
from PIL import Image, ImageOps

SLUG = "nkosi-thatchers"
ROOT = "wp-theme"
THEME = os.path.join(ROOT, SLUG)
ASSETS = os.path.join(THEME, "assets")

# ---- clean / scaffold ----
if os.path.exists(THEME):
    shutil.rmtree(THEME)
for d in (ASSETS, os.path.join(ASSETS, "js"), os.path.join(ASSETS, "fonts"), os.path.join(ASSETS, "images")):
    os.makedirs(d, exist_ok=True)

# ---- index.php from index.html ----
html = open("index.html", encoding="utf-8").read()

# shield the absolute OG image URL (contains 'images/') before the generic pass
html = html.replace("https://nkosithatchers.com/images/og-image.jpg", "%%OG%%")

# CSS + JS are enqueued via functions.php — drop the static tags
html = re.sub(r'\s*<link rel="stylesheet" href="css/styles\.css">', "", html)
html = re.sub(r'\s*<script src="js/main\.js" defer></script>', "", html)

# point font preload + favicons at the bundled theme assets
html = html.replace('href="fonts/bitter-700.woff2"', 'href="<?php echo $t; ?>/assets/fonts/bitter-700.woff2"')
html = html.replace('href="favicon.svg"', 'href="<?php echo $t; ?>/assets/favicon.svg"')
html = html.replace('href="favicon.ico"', 'href="<?php echo $t; ?>/assets/favicon.ico"')
html = html.replace('href="apple-touch-icon.png"', 'href="<?php echo $t; ?>/assets/apple-touch-icon.png"')

# every remaining images/ reference (src, srcset, href, data-full) -> theme assets
html = html.replace("images/", "<?php echo $t; ?>/assets/images/")
html = html.replace("%%OG%%", "<?php echo $t; ?>/assets/images/og-image.jpg")

# WordPress hooks
html = html.replace("</head>", "<?php wp_head(); ?>\n</head>")
html = html.replace("</body>", "<?php wp_footer(); ?>\n</body>")

index_php = "<?php $t = get_template_directory_uri(); ?>\n" + html
open(os.path.join(THEME, "index.php"), "w", encoding="utf-8").write(index_php)

# ---- style.css (theme header + our CSS, font path fixed) ----
css = open("css/styles.css", encoding="utf-8").read()
css = css.replace('url("../fonts/bitter-700.woff2")', 'url("assets/fonts/bitter-700.woff2")')
header = (
    "/*\n"
    "Theme Name: Nkosi Thatchers\n"
    "Theme URI: https://www.nkosi-thatchers.co.za\n"
    "Description: Single-page brochure theme for Nkosi Thatchers — thatch roofing across Gauteng, South Africa.\n"
    "Version: 1.0.0\n"
    "Requires at least: 5.0\n"
    "Tested up to: 6.6\n"
    "Requires PHP: 7.0\n"
    "License: GNU General Public License v2 or later\n"
    "License URI: https://www.gnu.org/licenses/gpl-2.0.html\n"
    "Text Domain: nkosi-thatchers\n"
    "*/\n\n"
)
open(os.path.join(THEME, "style.css"), "w", encoding="utf-8").write(header + css)

# ---- functions.php ----
functions = """<?php
/**
 * Nkosi Thatchers theme setup.
 */

// Enqueue the theme stylesheet and the site JS (in the footer, deferred).
function nkosi_enqueue_assets() {
    $ver = '1.0.0';
    wp_enqueue_style( 'nkosi-style', get_stylesheet_uri(), array(), $ver );
    wp_enqueue_script( 'nkosi-main', get_template_directory_uri() . '/assets/js/main.js', array(), $ver, true );
}
add_action( 'wp_enqueue_scripts', 'nkosi_enqueue_assets' );

// Add defer to the main script tag.
function nkosi_defer_script( $tag, $handle ) {
    if ( 'nkosi-main' === $handle ) {
        return str_replace( ' src', ' defer src', $tag );
    }
    return $tag;
}
add_filter( 'script_loader_tag', 'nkosi_defer_script', 10, 2 );

// Lightweight brochure: drop the emoji script/styles WordPress injects.
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );
"""
open(os.path.join(THEME, "functions.php"), "w", encoding="utf-8").write(functions)

# ---- copy assets ----
shutil.copy("js/main.js", os.path.join(ASSETS, "js", "main.js"))
shutil.copy("fonts/bitter-700.woff2", os.path.join(ASSETS, "fonts", "bitter-700.woff2"))
for f in glob.glob("images/*.webp") + glob.glob("images/*.jpg"):
    shutil.copy(f, os.path.join(ASSETS, "images", os.path.basename(f)))
for fav in ("favicon.svg", "favicon.ico", "apple-touch-icon.png"):
    if os.path.exists(fav):
        shutil.copy(fav, os.path.join(ASSETS, os.path.basename(fav)))

# ---- screenshot.png (shown in Appearance > Themes) 1200x900 ----
hero = ImageOps.exif_transpose(Image.open("images/originals/WhatsApp Image 2026-07-17 at 17.06.12.jpeg")).convert("RGB")
tw, th = 1200, 900
r = max(tw / hero.width, th / hero.height)
h2 = hero.resize((round(hero.width * r), round(hero.height * r)), Image.LANCZOS)
l = (h2.width - tw) // 2; t = (h2.height - th) // 2
h2.crop((l, t, l + tw, t + th)).save(os.path.join(THEME, "screenshot.png"))

# ---- zip it ----
zip_path = SLUG + "-theme.zip"
if os.path.exists(zip_path):
    os.remove(zip_path)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for base, _, files in os.walk(THEME):
        for name in files:
            full = os.path.join(base, name)
            arc = os.path.relpath(full, ROOT)  # -> nkosi-thatchers/...
            z.write(full, arc)

size = os.path.getsize(zip_path) / 1048576
print("Theme folder: %s" % THEME)
print("Uploadable zip: %s  (%.2f MB)" % (zip_path, size))
