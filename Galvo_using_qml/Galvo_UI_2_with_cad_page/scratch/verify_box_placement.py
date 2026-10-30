from PIL import Image

im = Image.open('scratch/debug_marathi_box.png')
rgb = im.convert('RGB')
w, h = rgb.size

cyan_pixels = []
for y in range(h):
    for x in range(w):
        r, g, b = rgb.getpixel((x, y))
        if r < 80 and g > 150 and b > 180:
            cyan_pixels.append((x, y))

print(f"Cyan pixels found: {len(cyan_pixels)}")
if cyan_pixels:
    cx_min = min(p[0] for p in cyan_pixels)
    cx_max = max(p[0] for p in cyan_pixels)
    cy_min = min(p[1] for p in cyan_pixels)
    cy_max = max(p[1] for p in cyan_pixels)
    print(f"Cyan box bounds: X={cx_min}..{cx_max}, Y={cy_min}..{cy_max}")

    crop_box = (max(0, cx_min - 60), max(0, cy_min - 80), min(w, cx_max + 60), min(h, cy_max + 60))
    crop_img = im.crop(crop_box)
    crop_img.save('scratch/marathi_verified.png')
    print("Saved scratch/marathi_verified.png")

    white_inside = []
    white_outside_above = []
    for y in range(cy_min - 60, cy_max + 20):
        for x in range(cx_min - 10, cx_max + 10):
            r, g, b = rgb.getpixel((x, y))
            if r > 200 and g > 200 and b > 200:
                if y < cy_min - 10:
                    white_outside_above.append((x, y))
                elif y >= cy_min and y <= cy_max:
                    white_inside.append((x, y))

    print(f"White text pixels inside box: {len(white_inside)}")
    print(f"White text pixels above box/HUD: {len(white_outside_above)}")
