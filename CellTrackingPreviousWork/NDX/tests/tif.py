from PIL import Image
import tifffile
import numpy as np


def create_tif_stack(image_paths, output_path):
    arrays = []

    for path in image_paths:
        image = Image.open(path)
        image = image.convert('L')

        width, height = image.size

        image = image.resize((width, height))

        array = np.array(image)

        arrays.append(array)

    tifffile.imsave(output_path, arrays[0], compress=0)


# create_tif_stack(['image-before.png', 'image-after.png'], 'stack1_10.tif')

create_tif_stack(['examples/image-before.png'], 'before.tif')
create_tif_stack(['examples/image-after.png'], 'after.tif')