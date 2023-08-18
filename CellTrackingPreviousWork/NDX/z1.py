import imagej
from scyjava import jimport, to_java

ij = imagej.init('/opt/Fiji.app')


TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
Model = jimport('fiji.plugin.trackmate.Model')
Settings = jimport('fiji.plugin.trackmate.Settings')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
Spot = jimport('fiji.plugin.trackmate.Spot')

# Initialize TrackMate settings
settings = Settings()
settings.detectorFactory = None  # we won't be using a detector
settings.trackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SparseLAPTrackerFactory')()

# Initialize a TrackMate model and logger
model = Model()

spots = SpotCollection()

spot1 = Spot(100, 100, 0, 10, 1)
spot2 = Spot(105, 105, 0, 10, 1)

spots.add(spot1, to_java(0))
spots.add(spot2, to_java(1))

model.setSpots(spots, True)

# Run TrackMate on the model
TrackMate(model, settings).process()
    
# Retrieve the tracks and output the results
tracks = model.getTrackModel().trackIDs(True)

print(tracks)