from scyjava import jimport, to_java
import numpy as np
import imagej
import cv2

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


def get_spots():
	masks = np.load('/home/elifast/Documents/Programs/NDX/masks.npy')

	spots = SpotCollection()
	
	for frame in range(len(masks)):
		mask = masks[frame]

		for cell in range(1, np.max(mask) + 1):
			cell_mask = mask == cell  # extract the binary mask for this cell
			
			y, x = np.mean(np.nonzero(cell_mask), axis=1)  # Calculate the centroid of the cell
			z = 0
			radius = 10  # TODO: change this to actual radius
			quality = 1  # store the line index, to later retrieve the ROI.

			spot = Spot(x, y, z, radius, quality)  # x, y, z, radius, quality
			spot.putFeature('POSITION_T', to_java(float(frame), type='double'))
			spots.add(spot, to_java(frame))

	return spots


def create_trackmate(imp):
	model = Model()
	model.setLogger(Logger.IJ_LOGGER)
	# model.setPhysicalUnits( cal.getUnit(), cal.getTimeUnit() )
	
	# Settings.
	settings = Settings(imp)

	# Create the TrackMate instance.
	trackmate = TrackMate(model, settings)

	# Skip detection and get spots manually
	spots = get_spots()
	model.setSpots( spots, False )
	
	# Configure detector. We put nothing here, since we already have the spots
	settings.detectorFactory = ManualDetectorFactory()
	settings.detectorSettings = {}
	settings.detectorSettings['RADIUS'] = 10.0
	
	# Configure tracker
	settings.trackerFactory = SimpleSparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['LINKING_MAX_DISTANCE'] 		= 300.0
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']	= 300.0
	settings.trackerSettings['MAX_FRAME_GAP']				= to_java(3)
	
	settings.initialSpotFilterValue = -1.0

	return trackmate


masks = np.load('/home/elifast/Documents/Programs/NDX/masks.npy')
imp = ij.py.to_imageplus(masks)

trackmate = create_trackmate(imp)

assert trackmate.process(), str(trackmate.getErrorMessage())

model = trackmate.getModel()
track_model = model.getTrackModel()

print(track_model)

# for track in track_model.trackIDs(True):
# 	track_spots = model.getTrackModel().trackSpots(track)
# 	track_duration = model.getTrackModel().trackDuration(track)
# 	print(f"Track {track}: {len(track_spots)} spots over frames")

# 	trackModel = model.getTrackModel()





# cv2.imshow('masks', masks[0] * 255)

# cv2.waitKey(0)
# cv2.destroyAllWindows()