import numpy as np
from scyjava import jimport, to_java
from detect import run_cellpose
import imagej

ij = imagej.init('/opt/Fiji.app')


TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
Model = jimport('fiji.plugin.trackmate.Model')
Settings = jimport('fiji.plugin.trackmate.Settings')
# Logger = jimport('fiji.plugin.trackmate.Logger')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
Spot = jimport('fiji.plugin.trackmate.Spot')
# TrackCollection = jimport('fiji.plugin.trackmate.TrackCollection')
# TrackIndexAnalyzer = jimport('fiji.plugin.trackmate.action.TrackIndexAnalyzer')

# Initialize TrackMate settings
settings = Settings()
settings.detectorFactory = None  # we won't be using a detector
settings.trackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')()
# settings.addSpotAnalyzerFactory(jimport('fiji.plugin.trackmate.features.spot.SpotIntensityAnalyzerFactory')())
# settings.addSpotAnalyzerFactory(jimport('fiji.plugin.trackmate.features.spot.SpotRadiusEstimatorFactory')())
# settings.addTrackAnalyzer(jimport('fiji.plugin.trackmate.features.track.TrackDurationAnalyzer')())

# Initialize a TrackMate model and logger
model = Model()
# logger = Logger()


masks = run_cellpose(gpu=True)

spots = SpotCollection()

for frame in range(len(masks['0'])):
    mask = masks['0'][frame]
    
    for i in range(1, np.max(mask) + 1):
        cell_mask = mask == i  # get the binary mask for this cell
        
        y, x = np.mean(np.nonzero(cell_mask), axis=1)  # calculate the centroid of the cell
        
        spot = Spot(x, y, 0, 10, 1)  # x, y, z, radius, quality
        spots.add(spot, to_java(frame))
    
    model.setSpots(spots, False)


print(model.getSpots())
    
# Run TrackMate on the model
TrackMate(model, settings).process()

print('dony')
    
# Retrieve the tracks and output the results
tracks = model.getTrackModel().trackIDs(True)

print(tracks)

for track in tracks:
    track_spots = model.getTrackModel().trackSpots(track)
    track_duration = model.getTrackModel().trackDuration(track)
    print(f"Track {track}: {len(track_spots)} spots over {track_duration} frames")

print('done')
