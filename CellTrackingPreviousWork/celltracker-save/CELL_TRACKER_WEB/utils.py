print(f'Importing libraries...')

from collections import defaultdict
from PIL import Image
import numpy as np
from cellpose import models
from scyjava import jimport, to_java
import imagej
import csv

print('Loading ImageJ...')
ij = imagej.init('/opt/Fiji.app')

print('Loading plugins...')
Logger = jimport('fiji.plugin.trackmate.Logger')
Model = jimport('fiji.plugin.trackmate.Model')
SelectionModel = jimport('fiji.plugin.trackmate.SelectionModel')
Settings = jimport('fiji.plugin.trackmate.Settings')
Spot = jimport('fiji.plugin.trackmate.Spot')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
ManualDetectorFactory = jimport('fiji.plugin.trackmate.detection.ManualDetectorFactory')
SimpleSparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleSparseLAPTrackerFactory')


def get_batch_identifier(path):
	filename = path.stem

	for index in range(-1, -1 * len(filename), -1):
		if filename[index] == '-':
			return filename[0:index]
	
	raise OSError(f'It appears that "{path.name}" was named incorrectly. Make sure it has the format "[batch_identifier]-[frame_number]"')


def organize_batches(images_directory):
	batches = defaultdict(list)

	for image_path in images_directory.iterdir():
		batches[get_batch_identifier(image_path)].append(image_path)

	for key in batches:
		batches[key] = sorted(batches[key], key=lambda x: int(str(x.stem).split('-')[-1]))
	
	return batches


def load_images(paths):
	return [np.array(Image.open(path).convert('L')) for path in paths]


def get_spots(masks):
	spot_collection = SpotCollection()

	for frame, mask in enumerate(masks):  # iterate over each frame
		for cell in range(1, mask.max() + 1):  # iterate over each cell in the mask
			coords = np.where(mask == cell)
	
			area = len(coords[0])

			radius = np.sqrt(area / np.pi)
			radius = radius.round()
			radius = radius.astype(int)

			center = np.mean(coords, axis=1)
			center = center.round()
			center = center.astype(int)

			y, x = center

			spot = Spot(x, y, 0, radius, 1)  # x, y, z, radius, quality
			spot.putFeature('POSITION_T', to_java(float(frame), type='double'))

			spot_collection.add(spot, to_java(frame))
	
	return spot_collection


def create_trackmate_settings(masks):
	image_plus = ij.py.to_imageplus(np.array(masks))

	settings = Settings(image_plus)

	# configure detector (we put nothing here, since we already have the spots)
	settings.detectorFactory = ManualDetectorFactory()
	settings.detectorSettings = {}
	settings.detectorSettings['RADIUS'] = 100.0
	
	# configure tracker
	settings.trackerFactory = SimpleSparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['LINKING_MAX_DISTANCE'] = 100.0
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 10.0
	settings.trackerSettings['MAX_FRAME_GAP'] = to_java(3)
	
	settings.initialSpotFilterValue = -1.0

	return settings


def create_trackmate_model(spots):
	model = Model()
	model.setLogger(Logger.VOID_LOGGER)

	model.setSpots(spots, False)

	return model


def track_cells(images_directory, gpu=False):
	cellpose_model = models.Cellpose(gpu=gpu, model_type='cyto2')
	
	print('Organizing batches...')

	batches = organize_batches(images_directory)

	for batch in batches:
		print('Loading images...')

		images = load_images(batches[batch])

		print('Detecting cells...')
		masks, _, _, _ = cellpose_model.eval(images, diameter=None, channels=(0, 0))

		spots = get_spots(masks)

		print('Starting TrackMate...')

		trackmate_settings = create_trackmate_settings(masks)
		trackmate_model = create_trackmate_model(spots)

		trackmate = TrackMate(trackmate_model, trackmate_settings)
		trackmate.process()

		return trackmate_model, masks


def get_track_information(trackmate_model):
	track_model = trackmate_model.getTrackModel()

	results = []

	for trackID in track_model.trackIDs(True):
		spots = track_model.trackSpots(trackID)
		spots = list(spots)

		spots_list = []

		for spot in spots:
			x = float(spot.getDoublePosition(0))
			y = float(spot.getDoublePosition(1))
			z = float(spot.getDoublePosition(2))

			spots_list.append((x, y, z))
		
		results.append(spots_list)
	
	return results


def save_to_csv(path, trackmate_model):
	track_model = trackmate_model.getTrackModel()

	track_information = np.empty((0, 6))

	for trackID in track_model.trackIDs(True):
		spots = list(track_model.trackSpots(trackID))

		start_x = float(spots[0].getDoublePosition(0))
		start_y = float(spots[0].getDoublePosition(1))
		end_x = float(spots[-1].getDoublePosition(0))
		end_y = float(spots[-1].getDoublePosition(1))
		distance_moved = np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
		slope = (end_y - start_y) / (end_x - start_x)

		track = np.array([start_x, start_y, end_x, end_y, distance_moved, slope])
		track_information = np.vstack([track_information, track])

	sorted_indices = np.argsort(np.abs(track_information[:, 5] - track_information[:, 5].mean()))
	track_information = track_information[sorted_indices]

	std_in_slope = track_information[:, 5].std()
	mean_slope = track_information[:, 5].mean()

	with open(path, 'w') as file:
		writer = csv.writer(file)

		writer.writerow(['START X', 'START Y', 'END X', 'END Y', 'DISTANCE MOVED', 'SLOPE', 'STANDARD DEVIATIONS AWAY FROM MEAN SLOPE'])

		for track in track_information:
			writer.writerow([*track, np.abs(track[5] - mean_slope) / std_in_slope])
	
		writer.writerow(['STANDARD DEVIATION IN SLOPE:', std_in_slope])
