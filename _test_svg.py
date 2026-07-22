try:
    import cairosvg
    print("cairosvg", cairosvg.__version__)
except Exception as e:
    print("cairosvg fail", e)

try:
    import io
    import ssl
    import urllib.request

    from PIL import Image

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = "https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/products/icons/sourcetree-neutral.svg"
    req = urllib.request.Request(url, headers={"User-Agent": "test/1.0"})
    svg = urllib.request.urlopen(req, context=ctx, timeout=20).read()
    png = cairosvg.svg2png(bytestring=svg, output_width=512, output_height=512)
    img = Image.open(io.BytesIO(png))
    print("render ok", img.size, img.mode)
except Exception as e:
    print("render fail", e)
