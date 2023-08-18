import imagej
from scyjava import jimport, to_java
# from detect import run_cellpose
import tifffile
import numpy as np

ij = imagej.init('/opt/Fiji.app')

Model = jimport('fiji.plugin.trackmate.Model')
Settings = jimport('fiji.plugin.trackmate.Settings')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
SimpleSparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleSparseLAPTrackerFactory')

masks = tifffile.imread('/home/elifast/Documents/Programs/NDX/masks.tif')
masks_plus = ij.py.to_imageplus(masks)



model = Model()
 
settings = Settings(masks_plus)
 
# Configure detector - We use the Strings for the keys
settings.detectorFactory = None
settings.detectorSettings = {
    'DO_SUBPIXEL_LOCALIZATION' : True,
    'RADIUS' : 2.5,
    'TARGET_CHANNEL' : 1,
    'THRESHOLD' : 0.,
    'DO_MEDIAN_FILTERING' : False,
}  
 
# Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SimpleSparseLAPTrackerFactory()
settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
settings.trackerSettings['ALLOW_TRACK_MERGING'] = True
 
# Add ALL the feature analyzers known to TrackMate. They will 
# yield numerical features for the results, such as speed, mean intensity etc.
settings.addAllAnalyzers()
 
 
trackmate = TrackMate(model, settings)

ok = trackmate.checkInput()
if not ok:
    print(str(trackmate.getErrorMessage()))
    quit()
 
ok = trackmate.process()
if not ok:
    print(str(trackmate.getErrorMessage()))
    quit()


print('yay')



# masks = run_cellpose(gpu=True)['0']
# masks = np.array(masks, dtype=np.uint8).clip(0, 1) * 255

# print(masks.shape)

# tifffile.imwrite('/home/elifast/Documents/Programs/NDX/masks.tif', masks)

# image_plus = ij.py.to_imageplus(masks)

# settings = Settings(image_plus)

# print(settings.detectorFactory)