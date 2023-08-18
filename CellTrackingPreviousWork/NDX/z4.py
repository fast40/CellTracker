import sys
from random import shuffle
import numpy as np

from scyjava import jimport, to_java
import imagej

ij = imagej.init('/opt/Fiji.app')



Logger = jimport('fiji.plugin.trackmate.Logger')
Model = jimport('fiji.plugin.trackmate.Model')
SelectionModel = jimport('fiji.plugin.trackmate.SelectionModel')
Settings = jimport('fiji.plugin.trackmate.Settings')
Spot = jimport('fiji.plugin.trackmate.Spot')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
ManualDetectorFactory = jimport('fiji.plugin.trackmate.detection.ManualDetectorFactory')
# LAPUtils = jimport('fiji.plugin.trackmate.tracking.LAPUtils')
# SpotAnalyzerProvider = jimport('fiji.plugin.trackmate.providers.SpotAnalyzerProvider')
# EdgeAnalyzerProvider = jimport('fiji.plugin.trackmate.providers.EdgeAnalyzerProvider')
# TrackAnalyzerProvider = jimport('fiji.plugin.trackmate.providers.TrackAnalyzerProvider')
# SparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.sparselap')
SimpleSparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleSparseLAPTrackerFactory')
# HyperStackDisplayer = jimport('fiji.plugin.trackmate.visualization.hyperstack')
# TrackMateGUIController = jimport('fiji.plugin.trackmate.gui')
# Jet = jimport('org.jfree.chart.renderer.InterpolatePaintScale')


def get_spots():
	masks = np.load('/home/elifast/Documents/Programs/NDX/masks.npy')

	spots = SpotCollection()
	
	for frame in range(len(masks)):
		mask = masks[frame]

		for cell in range(1, np.max(mask) + 1):
			cell_mask = mask == cell  # extract the binary mask for this cell
			
			y, x = np.mean(np.nonzero(cell_mask), axis=1)  # Calculate the centroid of the cell
			z = 0
			radius = 10  # TODO: change this to actual radius
			quality = 1  # store the line index, to later retrieve the ROI.

			spot = Spot(x, y, z, radius, quality)  # x, y, z, radius, quality

			spot = Spot( x, y, z, radius, quality )
			spot.putFeature('POSITION_T', to_java(float(frame), type='double'))
			spots.add(spot, to_java(frame))

	return spots


def create_trackmate(imp):
	model = Model()
	model.setLogger( Logger.IJ_LOGGER )
	# model.setPhysicalUnits( cal.getUnit(), cal.getTimeUnit() )
	
	# Settings.
	settings = Settings(imp)
	# settings.setFrom()
	
	# Create the TrackMate instance.
	trackmate = TrackMate( model, settings )
	
	# Add ALL the feature analyzers known to TrackMate, via
	# providers. 
	# They offer automatic analyzer detection, so all the 
	# available feature analyzers will be added. 
	# Some won't make sense on the binary image (e.g. contrast)
	# but nevermind.
	
	# spotAnalyzerProvider = SpotAnalyzerProvider()
	# for key in spotAnalyzerProvider.getKeys():
	# 	print( key )
	# 	settings.addSpotAnalyzerFactory( spotAnalyzerProvider.getFactory( key ) )
	
	# edgeAnalyzerProvider = EdgeAnalyzerProvider()
	# for  key in edgeAnalyzerProvider.getKeys():
	# 	print( key )
	# 	settings.addEdgeAnalyzer( edgeAnalyzerProvider.getFactory( key ) )
	
	# trackAnalyzerProvider = TrackAnalyzerProvider()
	# for key in trackAnalyzerProvider.getKeys():
	# 	print( key )
	# 	settings.addTrackAnalyzer( trackAnalyzerProvider.getFactory( key ) )
	
	# trackmate.getModel().getLogger().log( settings.toStringFeatureAnalyzersInfo() )
	# trackmate.computeSpotFeatures( True )
	# trackmate.computeEdgeFeatures( True )
	# trackmate.computeTrackFeatures( True )
	
	# Skip detection and get spots manually
	spots = get_spots()
	model.setSpots( spots, False )
	
	# Configure detector. We put nothing here, since we already have the spots 
	# from previous step.
	settings.detectorFactory = ManualDetectorFactory()
	settings.detectorSettings = {}
	settings.detectorSettings['RADIUS'] = 10.0
	
	# Configure tracker
	settings.trackerFactory = SimpleSparseLAPTrackerFactory()
	# settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['LINKING_MAX_DISTANCE'] 		= 300.0
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']	= 300.0
	settings.trackerSettings['MAX_FRAME_GAP']				= to_java(3)
	
	settings.initialSpotFilterValue = -1.

	return trackmate



def process( trackmate ):
	"""
	Execute the full process BUT for the detection step.
	"""
	# Check settings.
	ok = trackmate.checkInput()
	# Initial filtering
	# print( 'Spot initial filtering' )
	# ok = ok and trackmate.execInitialSpotFiltering()
	# # Compute spot features.
	# print( 'Computing spot features' )
	# ok = ok and trackmate.computeSpotFeatures( True ) 
	# # Filter spots.
	# print( 'Filtering spots' )
	# ok = ok and trackmate.execSpotFiltering( True )
	# # Track spots.
	print( 'Tracking' )
	ok = ok and trackmate.execTracking()
	# Compute track features.
	print( 'Computing track features' )
	ok = ok and trackmate.computeTrackFeatures( True )
	# Filter tracks.
	print( 'Filtering tracks' )
	ok = ok and trackmate.execTrackFiltering( True )
	# Compute edge features.
	print( 'Computing link features' )
	ok = ok and trackmate.computeEdgeFeatures( True )

	return ok


# def display_results_in_GUI( trackmate ):
# 	"""
# 	Creates and show a TrackMate GUI to configure the display 
# 	of the results. 

# 	This might not always be desriable in e.g. batch mode, but 
# 	this allows to save the data, export statistics in IJ tables then
# 	save them to CSV, export results to AVI etc...
# 	"""
	
# 	gui = TrackMateGUIController( trackmate )

# 	# Link displayer and GUI.
	
# 	model = trackmate.getModel()
# 	selectionModel = SelectionModel( model)
# 	displayer = HyperStackDisplayer( model, selectionModel, imp )
# 	gui.getGuimodel().addView( displayer )
# 	displaySettings = gui.getGuimodel().getDisplaySettings()
# 	for key in displaySettings.keySet():
# 		displayer.setDisplaySettings( key, displaySettings.get( key ) )
# 	displayer.render()
# 	displayer.refresh()
	
# 	gui.setGUIStateString( 'ConfigureViews' )



# def color_rois_by_track( trackmate, rm ):
# 	"""
# 	Colors the ROIs stored in the specified ROIManager rm using a color
# 	determined by the track ID they have.
	
# 	We retrieve the IJ ROI that matches the TrackMate Spot because in the
# 	latter we stored the index of the spot in the quality feature. This
# 	is a hack of course. On top of that, it supposes that the index of the 
# 	ROI in the ROIManager corresponds to the line in the ResultsTable it 
# 	generated. So any changes to the ROIManager or the ResultsTable is 
# 	likely to break things.
# 	"""
# 	model = trackmate.getModel()
# 	track_colors = {}
# 	track_indices = [] 
# 	for i in model.getTrackModel().trackIDs( True ):
# 		track_indices.append( i )
# 	shuffle( track_indices )
	
# 	index = 0
# 	for track_id in track_indices:
# 		color = Jet.getPaint( float(index) / ( len( track_indices) - 1 ) )
# 		track_colors[ track_id ] = color
# 		index = index + 1
	
# 	spots = model.getSpots()
# 	for spot in spots.iterable( True ):
# 		q = spot.getFeature( 'QUALITY' ) # Stored the ROI id.
# 		roi_id = int( q )
# 		roi = rm.getRoi( roi_id )
	
# 		# Get track id.
# 		track_id = model.getTrackModel().trackIDOf( spot )
# 		if track_id is None:
# 			color = Color.GRAY
# 		else:
# 			color = track_colors[ track_id ] 
			
# 		roi.setFillColor( color )



#------------------------------
# 			MAIN 
#------------------------------

# # Get current image.
# imp = WindowManager.getCurrentImage()

# # Remove overlay if any.
# imp.setOverlay( None )

# # Get results table.
# results_table = ResultsTable.getResultsTable()

# Create TrackMate instance.


imp = np.load('/home/elifast/Documents/Programs/NDX/masks.npy')
imp = ij.py.to_imageplus(imp)

trackmate = create_trackmate(imp)

#-----------------------
# Process.
#-----------------------

ok = process( trackmate )
if not ok:
	print('Error:', str(trackmate.getErrorMessage()))
	quit()


print('yay')

model = trackmate.getModel()
tracks = model.getTrackModel().trackIDs(True)

for track in tracks:
    track_spots = model.getTrackModel().trackSpots(track)
    # track_duration = model.getTrackModel().trackDuration(track)
    print(f"Track {track}: {len(track_spots)} spots over frames")

# #-----------------------
# # Display results.
# #-----------------------

# # Create the GUI and let it control display of results.
# display_results_in_GUI( trackmate )

# # Color ROI by track ID!
# rm = RoiManager.getInstance()
# color_rois_by_track( trackmate, rm )