import pathlib
import argparse
import pickle
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', default='results.bin', help='The path (or name) of the file containing the tracking data.')
parser.add_argument('-o', '--output', default='results.csv', help='The path (or name) of the csv file containing the results of the tracking.')
parser.add_argument('-f', '--filter', default='0', help='the number of standard deviations away from the mean direction to capture.')

args = parser.parse_args()

path = pathlib.Path(args.input).resolve()

with open(path, 'rb') as file:
    track_information, masks = pickle.load(file)


slopes = np.array([])

for track in track_information:
    (x1, y1, z1), (x2, y2, z2) = track

    slope = (y2 - y1) / (x2 - x1)

    slopes = np.append(slopes, slope)


values = np.abs(slopes - slopes.mean())
# print(np.where(values <= slopes.std()))

# print(values.argsort())

print(slopes[values.argsort()])



print(slopes.mean())
print(slopes.std())


def get_track_information_2(trackmate_model):
	track_model = trackmate_model.getTrackModel()

	track_information = np.array([])

	for i, trackID in enumerate(track_model.trackIDs(True)):
		spots = list(track_model.trackSppots(trackID))

		start_x = float(spots[0].getDoublePosition(0))
		start_y = float(spots[0].getDoublePosition(1))
		end_x = float(spots[-1].getDoublePosition(0))
		end_y = float(spots[-1].getDoublePosition(1))

		slope = (end_y - start_y) / (end_x - start_x)

		track_information.append(track_information, [i, start_x, start_y, end_x, end_y, slope])

	sorted_indices = np.argsort(track_information[:, 5] - track_information[:, 5].mean())

	return track_information[sorted_indices]

'''
cell x1 y1 x2 y2 slope distance from std



'''