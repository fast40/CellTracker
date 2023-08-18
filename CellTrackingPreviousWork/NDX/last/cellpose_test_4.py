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

# Loop over each frame and add spots for each cell mask
for frame in range(len(masks['0'])):
    mask = masks['0'][frame]

    spots = SpotCollection()  # Create a SpotCollection for this frame
    
    # Loop over each cell mask and add a Spot to the SpotCollection
    for i in range(1, np.max(mask) + 1):
        # Extract the binary mask for this cell
        cell_mask = mask == i
        
        # Calculate the centroid of the cell
        y, x = np.mean(np.nonzero(cell_mask), axis=1)
        
        # Add a Spot to the SpotCollection with the centroid coordinates and intensity
        spot = Spot(x, y, 0, 10, 1)  # x, y, z, radius, quality
        spots.add(spot, to_java(frame))
    
    # Add the SpotCollection to the model for this frame
    model.addSpots(spots, frame)
    
# Run TrackMate on the model
TrackMate(model, settings).process()
    
# Retrieve the tracks and output the results
tracks = model.getTrackModel().trackIDs(True)
for track in tracks:
    track_spots = model.getTrackModel().trackSpots(track)
    track_duration = model.getTrackModel().trackDuration(track)
    print(f"Track {track}: {len(track_spots)} spots over {track_duration} frames")
