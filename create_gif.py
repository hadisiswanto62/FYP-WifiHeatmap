# To combine images into gif
import imageio
from pathlib import Path

OUTPUT_PATH = Path('output')
HEATMAP_PATH = OUTPUT_PATH / 'heatmap'
GIF_PATH = OUTPUT_PATH / 'gif'

list_end_filter = [
    "All APs.png",
    "Non-NaN APs.png",
    "Relevant APs.png"
]
for end_filter in list_end_filter:
    images = []
    for filename in HEATMAP_PATH.iterdir():
        if ((filename.name.endswith(end_filter)) and ('Router data' not in filename.name)):
            images.append(imageio.imread(filename))
    imageio.mimsave(GIF_PATH / f'{end_filter[:-4]}.gif', images, duration=1)