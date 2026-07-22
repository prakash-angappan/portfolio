import re
import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

urls = [
    "https://upload.wikimedia.org/wikipedia/commons/0/00/PlayStation_logo.svg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/330px-PlayStation_logo.svg.png",
    "https://basecamp.com/assets/images/help/basecamp.png",
    "https://basecamp.com/assets/images/logo.svg",
    "https://raw.githubusercontent.com/basecamp/omarchy/main/assets/icons/basecamp.png",
    "https://raw.githubusercontent.com/basecamp/omarchy/main/assets/icons/basecamp.svg",
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=ua)
        r = urllib.request.urlopen(req, context=ctx, timeout=20)
        d = r.read()
        print(len(d), r.headers.get("content-type", ""), u)
    except Exception as e:
        print("ERR", u, e)

req = urllib.request.Request("https://basecamp.com/", headers=ua)
html = urllib.request.urlopen(req, context=ctx, timeout=20).read().decode("utf-8", "replace")
for m in sorted(set(re.findall(r'(?:src|href)="([^"]*(?:logo|icon|assets)[^"]*)"', html, re.I))):
    print("BC:", m)
