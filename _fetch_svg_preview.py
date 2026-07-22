import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {"User-Agent": "Mozilla/5.0"}

for name in ["sourcetree-neutral.svg", "jira-neutral.svg"]:
    url = f"https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/products/icons/{name}"
    req = urllib.request.Request(url, headers=ua)
    data = urllib.request.urlopen(req, context=ctx, timeout=20).read().decode("utf-8")
    print("===", name, "len", len(data), "===")
    print(data[:1200])
    print()
