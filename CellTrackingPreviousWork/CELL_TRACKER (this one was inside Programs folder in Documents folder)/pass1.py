import pathlib
from collections import defaultdict
from PIL import Image
import numpy as np
from cellpose import models
from scyjava import jimport, to_java
import imagej

ij = imagej.init('/opt/Fiji.app')

Logger = jimport('fiji.plugin.trackmate.Logger')
Model = jimport('fiji.plugin.trackmate.Model')
SelectionModel = jimport('fiji.plugin.trackmate.SelectionModel')
Settings = jimport('fiji.plugin.trackmate.Settings')
Spot = jimport('fiji.plugin.trackmate.Spot')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
ManualDetectorFactory = jimport('fiji.plugin.trackmate.detection.ManualDetectorFactory')
SimpleSparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleSparseLAPTrackerFactory')


def get_batch_identifier(image_path):
	"""
	Get the batch identifier for the given image.
	This should be the string that comes before the "-[frame_number]" in the file name

	:returns: the batch identifier for the given image
	"""

	filename = image_path.stem

	for index in range(-1, -1 * len(filename), -1):
		if filename[index] == '-':
			return filename[0:index]
	
	raise OSError(f'It appears that "{image_path.name}" was named incorrectly. Make sure it has the format "[batch_identifier]-[frame_number]"')


def get_batches(images_directory):
	"""
	Iterate over all paths in images_directory and sort them first by batch and then frame number

	:return: a `defaultdict` containing a `list` of paths sorted by frame for each batch identifier
	"""

	batches = defaultdict(list)

	for image_path in images_directory.iterdir():
		batches[get_batch_identifier(image_path)].append(image_path)

	for key in batches:
		batches[key] = sorted(batches[key], key=lambda x: int(str(x.stem).split('-')[-1]))
	
	return batches


def load_images(batches):
	"""
	Read the image files given by a dictionary of lists of image paths into numpy arrays

	:return: a `defaultdict` containing a `list` of images for each batch identifier
	"""

	images = defaultdict(list)

	for key in batches:
		for path in batches[key]:
			image = Image.open(path)
			image_grayscale = image.convert('L')
			image_grayscale = image_grayscale.transpose(Image.FLIP_TOP_BOTTOM)

			images[key].append(np.array(image_grayscale))
	
	return images


def get_masks(images, gpu=False):
	"""
	Given a dictionary of lists of image data, calculate the masks for each image.

	:return: A `dictionary` containing masks for each image
	"""

	model = models.Cellpose(gpu=gpu, model_type='cyto2')

	masks = {}

	for key in images:
		batch_masks, _, _, _ = model.eval(images[key], diameter=None, channels=[0, 0])

		masks[key] = np.array(batch_masks)
	
	return masks


def get_spots(masks):
	"""
	Given a dictionary of lists of cell masks, create a spot for each cell in each mask

	:return: A `dictionary` containing a `SpotCollection` representation of every cell in each batch
	"""

	spots = {}

	for batch in masks:
		spot_collection = SpotCollection()
	
		for frame in range(len(masks[batch])):
			mask = masks[batch][frame]

			for cell in range(1, np.max(mask) + 1):
				cell_mask = mask == cell  # extract the binary mask for this cell
				
				y, x = np.mean(np.nonzero(cell_mask), axis=1)  # calculate the centroid of the cell
				z = 0
				radius = 100  # set a radius of 100 for each cell; might want to change this to the actual radius in the future
				quality = 1  # could use this to store the cell # to later retrieve the ROI

				spot = Spot(x, y, z, radius, quality)  # x, y, z, radius, quality
				spot.putFeature('POSITION_T', to_java(float(frame), type='double'))
				spot_collection.add(spot, to_java(frame))
		
		spots[batch] = spot_collection

	return spots


def create_trackmate(masks, spots):
	model = Model()
	model.setLogger(Logger.IJ_LOGGER)

	image_plus = ij.py.to_imageplus(masks)

	settings = Settings(image_plus)
	trackmate = TrackMate(model, settings)

	model.setSpots(spots, False)
	
	# configure detector (we put nothing here, since we already have the spots)
	settings.detectorFactory = ManualDetectorFactory()
	settings.detectorSettings = {}
	settings.detectorSettings['RADIUS'] = 100.0
	
	# configure tracker
	settings.trackerFactory = SimpleSparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['LINKING_MAX_DISTANCE'] 		= 300.0
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']	= 300.0
	settings.trackerSettings['MAX_FRAME_GAP']				= to_java(3)
	
	settings.initialSpotFilterValue = -1.0

	return trackmate


def track_cells(images_directory, gpu=False):
	"""
	Track the cells in the images in images_directory
	"""

	print('Getting image batches...')
	batches = get_batches(images_directory)

	print('Loading images...')
	images = load_images(batches)

	print('Calculating cell masks...')
	masks = get_masks(images, gpu=gpu)

	print('Extracting cell locations...')
	spots = get_spots(masks)

	# sus amongus

	masks = masks['0']
	spots = spots['0']

	trackmate = create_trackmate(masks, spots)
	trackmate.process()

	model = trackmate.getModel()
	track_model = model.getTrackModel()

	for track in track_model.trackIDs(True):
		track_spots = model.getTrackModel().trackSpots(track)
		print(f"Track {track}: {len(track_spots)} spots over frames")

	# return spots


def main():
	working_directory = pathlib.Path('/home/elifast/Documents/Programs/NDX')
	images_directory = working_directory.joinpath('images')

	track_cells(images_directory)


if __name__ == '__main__':
	main()




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