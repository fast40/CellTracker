import imagej
import scyjava
from cellpose import models, io
import os
import numpy as np

ij = imagej.init('/opt/Fiji.app')

TrackMate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')
# LAPTracker = scyjava.jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleLAPTracker')
DefaultTrackerFactory = scyjava.jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')





model = models.Cellpose(gpu=True, model_type='cyto2')

filenames = ['before.tif', 'after.tif']

images = [io.imread(os.path.join('/home/elifast/Documents/Programs/NDX', filename)) for filename in filenames]

masks, _, _, _ = model.eval(images, diameter=None, channels=[0, 0])



# Initialize TrackMate
tm = TrackMate()
settings = tm.getSettings()
settings.trackerFactory = DefaultTrackerFactory()
# settings.trackerSettings = LAPTracker()
# settings.addTrackAnalyzerFactory(scyjava.jimport('fiji.plugin.trackmate.features.track.TrackDurationAnalyzerFactory')())

# # Add the images to TrackMate
# for i, img in enumerate(images):
#     imp = ij.py.to_java(img)
#     tm.getModel().addImage(imp)

# Add the cells to TrackMate
for i, mask in enumerate(masks):
    for j, cell in enumerate(mask):
        x, y = np.where(cell)
        t = i + 1
        spot = tm.getModel().addSpot(x.mean(), y.mean(), 0, 0, t)
        spot.putFeature('POSITION_X', x.mean())
        spot.putFeature('POSITION_Y', y.mean())
        spot.putFeature('RADIUS', 10)  # Set the cell radius to 10 pixels

# Run the tracking
ok = tm.execTracking()

# Get the tracking results
model = tm.getModel()
tracks = model.getTrackModel().trackIDs(True)

# Get the positions of the cells for each track
for track_id in tracks:
    track = model.getTrackModel().trackSpots(track_id)
    positions = []
    for spot in track:
        t, x, y = spot.getFeature("FRAME"), spot.getFeature("POSITION_X"), spot.getFeature("POSITION_Y")
        positions.append((t, x, y))
    print(f"Track {track_id}: {positions}")
