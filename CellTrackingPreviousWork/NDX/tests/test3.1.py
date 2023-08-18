import imagej
import tifffile
import scyjava
import numpy as np

# initialize ImageJ
ij = imagej.init('/opt/Fiji.app')

# load the two images
image1 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image1.tif')
image2 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image2.tif')

# create an ImagePlus object for each image
imageplus1 = ij.py.to_imageplus(image1)
imageplus2 = ij.py.to_imageplus(image2)

# create a TrackMate object
trackmate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')

# create a settings object with default settings
settings = scyjava.jimport('fiji.plugin.trackmate.Settings')()
settings.setFrom(imp=imageplus1)
settings.detectorFactory.setSelected('DOG Detector')
settings.detectorSettings = {
    'DOGVariance': 1.0,
    'DOGDoPresmooth': False,
    'DOGNormalize': True,
    'DOGPolarity': False,
    'DOGSnake': False
}
settings.trackerFactory.setSelected('SPADES Tracker')

# detect spots in the first image
model = scyjava.jimport('fiji.plugin.trackmate.Model')(imageplus1)
trackmate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')(model, settings)
ok = trackmate.checkInput()
if not ok:
    print(trackmate.getErrorMessage())
trackmate.execDetection()

# extract the spots from the model
spots1 = model.getSpots()

# detect spots in the second image
model = scyjava.jimport('fiji.plugin.trackmate.Model')(imageplus2)
trackmate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')(model, settings)
ok = trackmate.checkInput()
if not ok:
    print(trackmate.getErrorMessage())
trackmate.execDetection()

# extract the spots from the model
spots2 = model.getSpots()

# create a SpotCollection object for each set of spots
spot_collection1 = scyjava.jimport('fiji.plugin.trackmate.SpotCollection')()
for spot in spots1:
    spot_collection1.add(spot)
    
spot_collection2 = scyjava.jimport('fiji.plugin.trackmate.SpotCollection')()
for spot in spots2:
    spot_collection2.add(spot)

# create a SpotTracker object
tracker = scyjava.jimport('fiji.plugin.trackmate.tracking.spade.SpadesTracker')()

# track the spots over time
spot_collection1.setName('t=0')
spot_collection2.setName('t=1')
tracks = tracker.process(spot_collection1, spot_collection2)

# compute the displacement of each cell between the two images
displacements = np.zeros(len(tracks), dtype=np.float)
for i, track in enumerate(tracks):
    spot1 = track.getSpot(0)
    spot2 = track.getSpot(1)
    displacement = np.sqrt((spot1.getX() - spot2.getX())**2 + (spot1.getY() - spot2.getY())**2)
    displacements[i] = displacement

# print the displacement of each cell
for i, displacement in enumerate(displacements):
    print('Cell {}: {} pixels'.format(i, displacement))
