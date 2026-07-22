try:
    import io
    import ssl
    import urllib.request

    import pyvips
    from PIL import Image

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = "https://cdn.jsdelivr.net/npm/@atlassian/brand-logos@1.3.0/dist/products/icons/sourcetree-neutral.svg"
    req = urllib.request.Request(url, headers={"User-Agent": "test/1.0"})
    svg = urllib.request.urlopen(req, context=ctx, timeout=20).read()
    image = pyvips.Image.new_from_buffer(svg, "", dpi=300, scale=4)
    mem = image.write_to_buffer(".png")
    img = Image.open(io.BytesIO(mem))
    print("pyvips ok", img.size, img.mode)
except Exception as e:
    print("pyvips fail", e)
