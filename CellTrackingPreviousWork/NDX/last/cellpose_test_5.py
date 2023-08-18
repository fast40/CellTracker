import numpy as np
from scyjava import jimport

Model = jimport('fiji.plugin.trackmate.Model')
Settings = jimport('fiji.plugin.trackmate.Settings')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')


LogDetectorFactory = jimport('fiji.plugin.trackmate.detection.LogDetectorFactory')
SparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')
# FeatureFilter = jimport('fiji.plugin.trackmate.features.FeatureFilter')


model = Model()

settings = Settings()

# Configure tracker - We want to allow merges and fusions
settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
# settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
# settings.trackerSettings['ALLOW_TRACK_MERGING'] = True

# Add ALL the feature analyzers known to TrackMate. They will 
# yield numerical features for the results, such as speed, mean intensity etc.
# settings.addAllAnalyzers()


trackmate = TrackMate(model, settings)

#--------
# Process
#--------

ok = trackmate.checkInput()
if not ok:
    print(str(trackmate.getErrorMessage()))
    quit()

ok = trackmate.process()
if not ok:
    print(str(trackmate.getErrorMessage()))
    quit()





















# Loop over each frame and add spots for each cell mask
for frame in range(n_frames):
    # Load the image and mask for this frame
    image = io.imread(image_files[frame])
    mask = io.imread(mask_files[frame])
    
    # Create a SpotCollection for this frame
    spots = SpotCollection()
    
    # Loop over each cell mask and add a Spot to the SpotCollection
    for i in range(1, np.max(mask) + 1):
        # Extract the binary mask for this cell
        cell_mask = mask == i
        
        # Calculate the centroid of the cell
        y, x = np.mean(np.nonzero(cell_mask), axis=1)
        
        # Add a Spot to the SpotCollection with the centroid coordinates and intensity
        spot = Spot(x, y, 0, 10, np.sum(image[cell_mask]))
        spots.add(spot)
    
    # Add the SpotCollection to the model for this frame
    model.addSpots(spots, frame)
    
# Run TrackMate on the model
TrackMate(model, settings, logger).process()
    
# Retrieve the tracks and output the results
tracks = model.getTrackModel().trackIDs(True)
for track in tracks:
    track_spots = model.getTrackModel().trackSpots(track)
    track_duration = model.getTrackModel().trackDuration(track)
    print(f"Track {track}: {len(track_spots)} spots over {track_duration} frames")
