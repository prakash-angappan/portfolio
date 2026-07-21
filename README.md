# Prakash Angappan — Portfolio

Personal portfolio site (SPA) built from a static HTML/CSS/JS template. Content lives under [`portfolio/`](portfolio/).

## Local Development

This project uses a **Python-only** local server (no Vite, no Node/npm). The document root is `portfolio/`, so relative asset paths work the same as in production.

### Requirements

- Python 3.9+ (tested with 3.13)
- **No third-party packages** — the server uses the standard library only (`http.server` + polling-based file watch)

### Start the server

From the repository root:

```bash
python dev_server.py
```

On Windows you can also double-click or run:

```bat
start.bat
```

Optional flags:

```bash
python dev_server.py --port 8080          # custom port
python dev_server.py --no-browser         # don't auto-open a tab
python dev_server.py --host 0.0.0.0       # listen on all interfaces
python dev_server.py --poll 0.25          # faster filesystem polling
```

### Default URL

Open **[http://127.0.0.1:5500/](http://127.0.0.1:5500/)** — this serves `portfolio/index.html`.

### Live reload

Editing files under `portfolio/` (HTML, CSS, JS, JSON, images, fonts, PDF, etc.) triggers an automatic browser refresh. Watching is done with lightweight polling (no `watchdog` install required). Stop the server with `Ctrl+C`.

### Friendly 404s

Missing assets during development return a simple HTML 404 page with a link back home, instead of a bare error.

## Project layout

```
portfolio/
  index.html      # SPA shell
  style.css
  script.js
  home.json
  projects.json
  contact.json
  favicon.svg
  images/
  *.pdf           # resume
dev_server.py     # local static server + live reload
start.bat         # Windows convenience launcher
```

## Deploy

This is a static site. Upload (or sync) the contents of `portfolio/` to any static host — for example GitHub Pages, Netlify, Cloudflare Pages, S3 + CloudFront, or a plain nginx/Apache document root. Point the host’s publish directory at `portfolio/` (or copy those files to the web root). No build step is required.
