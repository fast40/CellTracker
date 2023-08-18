import pathlib
from collections import defaultdict
from PIL import Image
import numpy as np
from cellpose import models


def get_batch_identifier(image_path):
    filename = image_path.stem

    for index in range(-1, -1 * len(filename), -1):
        if filename[index] == '-':
            return filename[0:index]
    
    raise OSError(f'It appears that "{image_path.name}" was named incorrectly. Make sure it has the format "[experiment_id]-[frame_number]"')


def get_batches(images_directory):
    batches = defaultdict(list)

    for image_path in images_directory.iterdir():
        batches[get_batch_identifier(image_path)].append(image_path)

    for key in batches:
        batches[key] = sorted(batches[key], key=lambda x: int(str(x.stem).split('-')[-1]))
    
    return batches


def load_images(batches):
    images = defaultdict(list)

    for key in batches:
        for path in batches[key]:
            image = Image.open(path)
            image_grayscale = image.convert('L')
            image_grayscale = image_grayscale.transpose(Image.FLIP_TOP_BOTTOM)

            images[key].append(np.array(image_grayscale))
    
    return images


def get_masks(images, gpu=False):
    model = models.Cellpose(gpu=gpu, model_type='cyto2')

    final_masks = {}

    for key in images:
        masks, _, _, _ = model.eval(images[key], diameter=None, channels=[0, 0])

        final_masks[key] = masks
        # final_masks[key] = final_masks[key].astype('uint8')
    
    return final_masks


def run_cellpose(gpu=False):
    # working_directory = pathlib.Path().resolve()
    working_directory = pathlib.Path('/home/elifast/Documents/Programs/NDX')
    images_directory = working_directory.joinpath('images')

    print('Getting image batches...')
    batches = get_batches(images_directory)

    print('Loading images...')
    images = load_images(batches)

    print('Calculating cell locations...')
    masks = get_masks(images, gpu=gpu)

    return masks
