# Nkosi Thatchers — WordPress theme

The static site is packaged as a self-hosted WordPress theme. It renders the
brochure exactly as the standalone site (same design, gallery lightbox, form).

## Build / rebuild the theme

```bash
py build_wp_theme.py
```

Produces `nkosi-thatchers-theme.zip` (and the unpacked `wp-theme/nkosi-thatchers/`).
Re-run it any time you change `index.html`, the CSS, or images.

## Install (self-hosted WordPress)

1. **WP Admin → Appearance → Themes → Add New → Upload Theme.**
2. Choose `nkosi-thatchers-theme.zip` → **Install Now** → **Activate.**
3. Visit your site — the brochure shows on the homepage.

> **If the upload is rejected for size** (the zip is ~10 MB and some hosts cap
> uploads at 2–8 MB): either raise `upload_max_filesize` / `post_max_size` in
> your host's PHP settings, **or** upload by FTP — unzip locally and copy the
> `nkosi-thatchers` folder into `wp-content/themes/`, then Activate in step 2.

## After activating — 2 things

1. **Formspree ID** (makes the contact form work):
   **Appearance → Theme File Editor → `index.php`**, find
   `action="https://formspree.io/f/YOUR_FORM_ID"`, replace `YOUR_FORM_ID` with
   your ID, **Update File**. (Or paste it into `index.html` and re-run the build
   before uploading.)

2. **Favicon**: already set by the theme. If you prefer WordPress to manage it,
   use **Appearance → Customize → Site Identity → Site Icon**.

## Notes

- **One-page theme.** It uses `index.php` as the template, so the brochure is
  the homepage (and the fallback for any URL). Fine for a single-page site. If
  you later want a blog or editable pages, that's the "owner-editable" route —
  a bigger conversion.
- **SEO plugins (Yoast / Rank Math):** the theme's `<head>` already contains the
  title, meta description, Open Graph, Twitter and LocalBusiness JSON-LD. If you
  run an SEO plugin it may output its own title/OG tags and duplicate these.
  Either skip the SEO plugin on this page, or strip the hardcoded tags from
  `index.php` and let the plugin manage them.
- **What's inside:** `style.css` (theme header + all CSS), `index.php` (the
  page), `functions.php` (enqueues CSS/JS, drops WP emoji cruft), `assets/`
  (JS, self-hosted font, web images, favicons), `screenshot.png` (admin preview).
- The theme is a **generated artifact** — it's git-ignored. The source of truth
  is `index.html` + `build_wp_theme.py`.
