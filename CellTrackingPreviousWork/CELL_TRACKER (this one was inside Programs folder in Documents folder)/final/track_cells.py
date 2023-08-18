import pathlib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', default='images', help='The path (or name) of the folder containing images to be analyzed.')
parser.add_argument('-o', '--output', default='results', help='The path (or name) of the binary file containing the results of the tracking. This file exists for the sole purpose of being processed further to generate a csv file.')
parser.add_argument('-g', '--gpu', action='store_true', help='Indicates that the program should use GPU.')

args = parser.parse_args()

path = pathlib.Path(args.input).resolve()
directory = path.parent

from utils import get_track_information, track_cells, save_to_csv

trackmate_model, masks = track_cells(path, gpu=args.gpu)
track_information = get_track_information(trackmate_model)

print('Saving results...')

save_to_csv(directory / f'{args.output}.csv', trackmate_model)

print(f'Results saved in "{args.output}.csv"')
