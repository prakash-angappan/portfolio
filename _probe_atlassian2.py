import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {"User-Agent": "Mozilla/5.0"}

urls = [
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/favicon-32x32.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/favicon-196x196.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/sourcetree/android-chrome-192x192.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/jira/favicon-32x32.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/jira/favicon-196x196.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/jira/android-chrome-192x192.png",
    "https://wac-cdn.atlassian.com/assets/img/favicons/atlassian/favicon-32x32.png",
    "https://cdn.jsdelivr.net/npm/@atlaskit/logo@5.8.0/dist/esm/ui/logo/jira-icon/index.js",
    "https://cdn.jsdelivr.net/npm/@atlaskit/logo@5.8.0/dist/cjs/ui/logo/jira-icon/index.js",
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=ua)
        r = urllib.request.urlopen(req, context=ctx, timeout=20)
        d = r.read()
        print(len(d), r.headers.get("content-type", ""), u)
    except Exception as e:
        print("ERR", u, e)
