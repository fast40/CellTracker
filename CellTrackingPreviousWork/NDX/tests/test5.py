import imagej
import tifffile
import scyjava
import numpy as np

# Initialize ImageJ
ij = imagej.init('/opt/Fiji.app')

# Read images
image1 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image1.tif')
image2 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image2.tif')

# Create ImagePlus objects
imageplus1 = ij.py.to_imageplus(image1)
imageplus2 = ij.py.to_imageplus(image2)

# Create TrackMate object
TrackMate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')
trackmate = TrackMate()

# Create Settings object
Settings = scyjava.jimport('fiji.plugin.trackmate.Settings')
settings = Settings(imageplus1)

# # Set parameters
# settings.detectorFactory = scyjava.jimport('fiji.plugin.trackmate.detection.LogDetectorFactory')()
# settings.detectorSettings = { 'DO_SUBPIXEL_LOCALIZATION' : True }
# settings.detectorSettings['RADIUS'] = 5.0
# settings.detectorSettings['TARGET_CHANNEL'] = 1
# settings.detectorSettings['THRESHOLD'] = 0.0

# settings.trackerFactory = scyjava.jimport('fiji.plugin.trackmate.tracking.sparselap.SparseLAPTrackerFactory')()
# settings.trackerSettings = { 'LINKING_MAX_DISTANCE' : 10.0, 'GAP_CLOSING_MAX_DISTANCE' : 10.0, 'MAX_FRAME_GAP' : 0 }
# settings.addTrackAnalyzer(scyjava.jimport('fiji.plugin.trackmate.features.track.TrackDurationAnalyzer')())

# # Set input image
# settings.imp = imageplus1

# Detect cells in first image
model = scyjava.jimport('fiji.plugin.trackmate.Model')()
spots = scyjava.jimport('fiji.plugin.trackmate.detection.Detector')().process(imageplus1, settings, model)

# # Track cells in second image
# settings.imp = imageplus2
# model.setPhysicalUnits('pixel')
# trackmate.execTrack(model, settings)

# # Get results
# spot_collection = model.getSpots()
# tracks = model.getTrackModel().trackIDs(True)

# # Calculate cell displacements
# for track_id in tracks:
#     track = model.getTrackModel().trackSpots(track_id)
#     if len(track) == 2:
#         spot1 = spot_collection.get(track[0])
#         spot2 = spot_collection.get(track[1])
#         displacement = np.sqrt((spot2.getFeature('POSITION_X') - spot1.getFeature('POSITION_X'))**2 + (spot2.getFeature('POSITION_Y') - spot1.getFeature('POSITION_Y'))**2)
#         print(f"Cell {track_id}: displacement = {displacement:.2f}")
