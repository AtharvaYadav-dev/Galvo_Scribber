from PIL import Image

im = Image.open('scratch/debug_marathi_box.png')
w, h = im.size
# Center of canvas is around (w * 0.45, h * 0.5)
box = (int(w * 0.25), int(h * 0.25), int(w * 0.70), int(h * 0.75))
crop = im.crop(box)
crop.save('scratch/crop_marathi.png')
print("Cropped saved")

