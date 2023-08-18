import imagej
import tifffile

# Initialize ImageJ
ij = imagej.init('/opt/Fiji.app')

# Load the image sequence
# imp = ij.io().openImage('stack.tif')
imp = tifffile.imread('/home/elifast/Documents/Programs/NDX/stack.tif')


# Create a TrackMate instance
tm = ij.plugin().createInstance("fiji.plugin.trackmate.Tracker")

# Configure TrackMate
settings = tm.getDefaultSettings()
settings.detectorFactory = ij.plugin().getPlugin("LogDetectorFactory")
settings.detectorSettings = { "DO_SUBPIXEL_LOCALIZATION": True }
settings.addSpotAnalyzerFactory(ij.plugin().getPlugin("SpotIntensityAnalyzerFactory"))

# Run TrackMate
ok = tm.process(imp)

# Extract the tracks
model = tm.getModel()
tracks = model.getTrackModel().trackIDs(True)

# Print the results
for track_id in tracks:
    track = model.getTrackModel().trackSpots(track_id)
    distance = 0.0
    for i in range(len(track)-1):
        pos1 = track.get(i).getFeature("POSITION_X"), track.get(i).getFeature("POSITION_Y")
        pos2 = track.get(i+1).getFeature("POSITION_X"), track.get(i+1).getFeature("POSITION_Y")
        distance += ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)**0.5
    print(f'Track {track_id} moved {distance:.2f} pixels.')
