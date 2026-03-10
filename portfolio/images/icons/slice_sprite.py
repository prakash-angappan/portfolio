from PIL import Image
import os

# get script folder automatically
script_dir = os.path.dirname(os.path.abspath(__file__))

sprite_path = os.path.join(script_dir, "icon_sprite_sheet.png")

output_folder = os.path.join(script_dir, "icons")
os.makedirs(output_folder, exist_ok=True)

icon_size = 256

sprite = Image.open(sprite_path)

index = 0

for y in range(0, sprite.height, icon_size):
    for x in range(0, sprite.width, icon_size):

        box = (x, y, x + icon_size, y + icon_size)
        icon = sprite.crop(box)

        filename = f"icon_{index}.png"
        icon.save(os.path.join(output_folder, filename))

        index += 1

print("Icons created successfully.")