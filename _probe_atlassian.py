import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

urls = [
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/apple-touch-icon-152x152.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/favicon-32x32.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/favicon-96x96.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/jira/apple-touch-icon-152x152.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/jira/favicon-96x96.png",
    "https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/favicons/fav-jira.png",
    "https://cdn.jsdelivr.net/npm/@atlaskit/logo@5.8.0/dist/esm/ui/logo/sourcetree-icon/index.js",
    "https://developer.atlassian.com/platform/marketplace/images/default-listing-logo.svg",
    "https://www.sourcetreeapp.com/enterprise/images/st-logo-icon.svg",
    "https://www.atlassian.com/dam/jcr:content/sourcetree-icon.svg",
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=ua)
        r = urllib.request.urlopen(req, context=ctx, timeout=20)
        d = r.read()
        print(len(d), r.headers.get("content-type", ""), u)
    except Exception as e:
        print("ERR", u, e)
