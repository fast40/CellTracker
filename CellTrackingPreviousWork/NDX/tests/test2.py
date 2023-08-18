import imagej
import tifffile
import scyjava

ij = imagej.init('/opt/Fiji.app')
 
image = tifffile.imread('/home/elifast/Documents/Programs/NDX/stack.tif')
image_plus = ij.py.to_imageplus(image)

TrackMate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')
Model = scyjava.jimport('fiji.plugin.trackmate.Model')
Settings = scyjava.jimport('fiji.plugin.trackmate.Settings')
LogDetectorFactory = scyjava.jimport('fiji.plugin.trackmate.detection.LogDetectorFactory')
SparseLAPTrackerFactory = scyjava.jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')
FeatureFilter = scyjava.jimport('fiji.plugin.trackmate.features.FeatureFilter')

model = Model()




settings = Settings(image_plus)
 
# Configure detector - We use the Strings for the keys
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings['DO_SUBPIXEL_LOCALIZATION'] = True
settings.detectorSettings['RADIUS'] = 7.5
settings.detectorSettings['TARGET_CHANNEL'] = scyjava.to_java(1)
settings.detectorSettings['THRESHOLD'] = 0.9
settings.detectorSettings['DO_MEDIAN_FILTERING'] = False


# Configure spot filters - Classical filter on quality
filter1 = FeatureFilter('QUALITY', 30, True)
settings.addSpotFilter(filter1)
 
# Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
settings.trackerSettings['ALLOW_TRACK_MERGING'] = True
 
# Add ALL the feature analyzers known to TrackMate. They will 
# yield numerical features for the results, such as speed, mean intensity etc.
settings.addAllAnalyzers()
 
# Configure track filters - We want to get rid of the two immobile spots at
# the bottom right of the image. Track displacement must be above 10 pixels.
 
filter2 = FeatureFilter('TRACK_DISPLACEMENT', 10, True)
settings.addTrackFilter(filter2)

















#-------------------
# Instantiate plugin
#-------------------
 
trackmate = TrackMate(model, settings)
 
#--------
# Process
#--------
 
ok = trackmate.checkInput()
if not ok:
    raise Exception(str(trackmate.getErrorMessage()))
 
ok = trackmate.process()
if not ok:
    raise Exception(str(trackmate.getErrorMessage()))

 
# #----------------
# # Display results
# #----------------
 
# # A selection.
# selectionModel = SelectionModel( model )
 
# # Read the default display settings.
# ds = DisplaySettingsIO.readUserDefault()
 
# displayer =  HyperStackDisplayer( model, selectionModel, imp, ds )
# displayer.render()
# displayer.refresh()
 
# # Echo results with the logger we set at start:
# model.getLogger().log( str( model ) )