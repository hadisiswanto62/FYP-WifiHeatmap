from PIL import Image, ImageDraw
from pathlib import Path

IMAGE_PATH = Path('data') / 'N4-02b.png'
MAP_OUTPUT_DIR = Path('output') / 'map'

im = Image.open(IMAGE_PATH)
draw = ImageDraw.Draw(im)
#x0 y0 
draw.line((0, 25, 50, 100), fill=128)

im.save(MAP_OUTPUT_DIR / 'test1.png')