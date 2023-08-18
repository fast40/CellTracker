import imagej
import tifffile
import numpy as np
import scyjava

ij = imagej.init('/opt/Fiji.app')

# Load the first image
image1 = tifffile.imread('/home/elifast/Documents/Programs/NDX/stack.tif')

# Load the second image
image2 = tifffile.imread('/home/elifast/Documents/Programs/NDX/stack2.tif')

# Convert the images to ImagePlus objects
imageplus1 = ij.py.to_imageplus(image1)
imageplus2 = ij.py.to_imageplus(image2)

# Create a SpotCollection object
spot_collection = scyjava.jimport('fiji.plugin.trackmate.SpotCollection')()

# Add the spots from the first image to the SpotCollection object
for x, y in np.ndindex(image1.shape[:2]):
    intensity = image1[x, y]
    spot = scyjava.jimport('fiji.plugin.trackmate.Spot')(x, y, 0, 1, intensity)
    spot_collection.add(spot)

# Initialize TrackMate
trackmate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')()
trackmate.setSpotCollection(spot_collection)
trackmate.getModel().setPhysicalUnits('pixel', 'pixel', 'frame', 1)

# Set the second image as the current frame in TrackMate
trackmate.getModel().setSourceImage(imageplus2)

# Run TrackMate
trackmate.execTracking()

# Retrieve the track data from TrackMate
track_model = trackmate.getModel().getTrackModel()
track_list = track_model.trackIDs(True)
for track_id in track_list:
    track = track_model.trackSpots(track_id)
    for spot in track:
        print(f'Track ID: {track_id}, X: {spot.getDoublePosition(0)}, Y: {spot.getDoublePosition(1)}, Z: {spot.getDoublePosition(2)}')
