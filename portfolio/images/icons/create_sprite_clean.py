from PIL import Image
import numpy as np

icons = [
"unreal.png",
"vicious-cycle.png",
"windows.png",
"android.png",
"blitzmax.png",
"godot.png",
"googleplay.png",
"html5.png",
"ios.png",
"phyre-engine.png",
"ps2.png",
"ps3move.png",
"psp.png",
"steam.png",
"torque.png",
"unity.png"
]

cell = 256
cols = 4
rows = 4

sprite = Image.new("RGBA", (cell*cols, cell*rows), (0,0,0,0))

def crop_icon(img):

    arr = np.array(img)

    rgb = arr[:,:,:3]
    alpha = arr[:,:,3]

    # detect real pixels (ignore white/transparent)
    mask = (alpha > 10) & (
        (rgb[:,:,0] < 240) |
        (rgb[:,:,1] < 240) |
        (rgb[:,:,2] < 240)
    )

    coords = np.column_stack(np.where(mask))

    if len(coords) == 0:
        return img

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    return img.crop((x0, y0, x1+1, y1+1))


for i, icon in enumerate(icons):

    img = Image.open(icon).convert("RGBA")

    # remove padding
    img = crop_icon(img)

    w, h = img.size

    # scale icon to fill 85% of cell
    scale = min((cell*0.85)/w, (cell*0.85)/h)

    nw = int(w*scale)
    nh = int(h*scale)

    img = img.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (cell, cell), (0,0,0,0))
    canvas.paste(img, ((cell-nw)//2, (cell-nh)//2), img)

    x = (i % cols) * cell
    y = (i // cols) * cell

    sprite.paste(canvas, (x,y), canvas)

sprite.save("sprite_1024_clean.png")

print("Done: sprite_1024_clean.png created")