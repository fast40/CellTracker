

import imagej
import tifffile
import scyjava

ij = imagej.init('/opt/Fiji.app')

image1 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image1.tif')
image2 = tifffile.imread('/home/elifast/Documents/Programs/NDX/image2.tif')

image1 = ij.py.to_imageplus(image1)
image2 = ij.py.to_imageplus(image2)

TrackMate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')
Model = scyjava.jimport('fiji.plugin.trackmate.Model')
Settings = scyjava.jimport('fiji.plugin.trackmate.Settings')
LogDetectorFactory = scyjava.jimport('fiji.plugin.trackmate.detection.LogDetectorFactory')
SparseLAPTrackerFactory = scyjava.jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')

model = Model()




# Create TrackMate instance
trackmate_module = TrackMate()

# Configure settings
settings = trackmate_module.getDefaultSettings()
settings.detectorFactory = trackmate.DetectorKeys.RECTANGLE_DETECTOR
settings.detectorSettings = {
    "RADIUS": 5.0,
    "THRESHOLD": 0.0,
    "DO_MEDIAN_FILTERING": False,
    "TARGET_CHANNEL": int(1),
    "DO_SUBPIXEL_LOCALIZATION": True,
}
settings.trackerFactory = trackmate.TrackerKeys.CELL_TRACKER
settings.trackerSettings = {
    "LINKING_MAX_DISTANCE": 10.0,
    "LINKING_FEATURE_PENALTIES": None,
    "GAP_CLOSING_MAX_DISTANCE": 10.0,
    "GAP_CLOSING_FEATURE_PENALTIES": None,
    "MAX_FRAME_GAP": 1,
}

# Create logger
logger = Logger.IJ_LOGGER

# Run TrackMate
trackmate_module.setLogger(logger)
trackmate_module.setSettings(settings)
trackmate_module.process(image1, image2)

# Get results table
results_table = ResultsTable.getResultsTable()

# Save results table
output_path = os.path.abspath("path/to/output")
output_file = os.path.join(output_path, "results.csv")

results_table.save(output_file)
