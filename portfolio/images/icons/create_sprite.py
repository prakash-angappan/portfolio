from PIL import Image
import os

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

for i, icon in enumerate(icons):

    img = Image.open(icon).convert("RGBA")

    w,h = img.size
    scale = min(cell/w, cell/h)

    nw = int(w*scale)
    nh = int(h*scale)

    img = img.resize((nw,nh), Image.LANCZOS)

    canvas = Image.new("RGBA",(cell,cell),(0,0,0,0))
    canvas.paste(img,((cell-nw)//2,(cell-nh)//2),img)

    x = (i % cols) * cell
    y = (i // cols) * cell

    sprite.paste(canvas,(x,y),canvas)

sprite.save("sprite_1024.png")

print("Sprite created: sprite_1024.png")