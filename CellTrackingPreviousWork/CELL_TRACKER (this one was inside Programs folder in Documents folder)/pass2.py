import pathlib
from collections import defaultdict
from PIL import Image
import numpy as np
from cellpose import models
from scyjava import jimport, to_java
import imagej

print('initializing imagej...')
ij = imagej.init('/opt/Fiji.app')

print('importing plugins...')
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


def get_batches(images_directory):
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
			cell_mask = mask == cell

			y, x = np.mean(np.nonzero(cell_mask), axis=1)

			spot = Spot(x, y, 0, 100, 1)  # x, y, z, radius, quality (may want to change radius to actual radius in the future)
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
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 100.0
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

	batches = get_batches(images_directory)

	for batch in batches:
		images = load_images(batches[batch])

		masks, flows, styles, diams = cellpose_model.eval(images, diameter=None, channels=(0, 0))

		print('-----diams-----')
		print(type(flows))
		print(len(flows))
		print(len(flows[0]))
		print(len(flows[1]))
		print('[][][][]')
		print(len(flows[0][0]))
		print(len(flows[0][1]))
		print(len(flows[0][2]))
		print(len(flows[0][3]))
		print('----------')

		spots = get_spots(masks)

		trackmate_settings = create_trackmate_settings(masks)
		trackmate_model = create_trackmate_model(spots)

		trackmate = TrackMate(trackmate_model, trackmate_settings)
		trackmate.process()

		return trackmate_model, masks


def main(gpu=False):
	working_directory = pathlib.Path('/home/elifast/Documents/Programs/NDX')
	images_directory = working_directory.joinpath('images')

	return track_cells(images_directory, gpu=gpu)


if __name__ == '__main__':
	main(gpu=True)




# masks = np.load('/home/elifast/Documents/Programs/NDX/masks.npy')
# imp = ij.py.to_imageplus(masks)

# trackmate = create_trackmate(imp)

# assert trackmate.process(), str(trackmate.getErrorMessage())

# model = trackmate.getModel()
# track_model = model.getTrackModel()

# print(track_model)

# for track in track_model.trackIDs(True):
# 	track_spots = model.getTrackModel().trackSpots(track)
# 	track_duration = model.getTrackModel().trackDuration(track)
# 	print(f"Track {track}: {len(track_spots)} spots over frames")

# 	trackModel = model.getTrackModel()





# cv2.imshow('masks', masks[0] * 255)

# cv2.waitKey(0)
# cv2.destroyAllWindows()