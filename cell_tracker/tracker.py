USE_GPU = True

print(f'Importing libraries...')

from cell_tracker import experiments
from PIL import Image
import numpy as np
from cellpose import models
from scyjava import jimport, to_java
import imagej
import csv
import cv2

print('Loading ImageJ...')
ij = imagej.init('/opt/Fiji.app')

print('Loading plugins...')
Logger = jimport('fiji.plugin.trackmate.Logger')
Model = jimport('fiji.plugin.trackmate.Model')
SelectionModel = jimport('fiji.plugin.trackmate.SelectionModel')
Settings = jimport('fiji.plugin.trackmate.Settings')
Spot = jimport('fiji.plugin.trackmate.Spot')
SpotCollection = jimport('fiji.plugin.trackmate.SpotCollection')
TrackMate = jimport('fiji.plugin.trackmate.TrackMate')
ManualDetectorFactory = jimport('fiji.plugin.trackmate.detection.ManualDetectorFactory')
SimpleSparseLAPTrackerFactory = jimport('fiji.plugin.trackmate.tracking.jaqaman.SimpleSparseLAPTrackerFactory')

print('Getting CellPose model')
cellpose_model = models.Cellpose(gpu=USE_GPU, model_type='cyto2')


def load_experiment_images(experiment_id):
    experiment_images = []
    experiments_directory_path = experiments.get_experiment_directory_path(experiment_id)

    for path in experiments_directory_path.iterdir():
        if 'before' not in path.name and 'after' not in path.name:
            continue

        image = Image.open(path)
        image_grayscale = image.convert('L')  # L is for "Lumanance" (converts image to a single channel which is "normally interpreted as grayscale")
        image_numpy = np.array(image_grayscale)

        experiment_images.append(image_numpy)

    return experiment_images


def get_masks(images):
    masks, _, _, _ = cellpose_model.eval(images, diameter=None, channels=(0, 0))

    return masks


def get_spots(masks):
    spot_collection = SpotCollection()

    for frame, mask in enumerate(masks):  # iterate over each frame
        for cell in range(1, mask.max() + 1):  # iterate over each cell in the mask
            coords = np.where(mask == cell)
    
            area = len(coords[0])

            center = np.mean(coords, axis=1)
            center = center.round()
            center = center.astype(int)

            y, x = center

            spot = Spot(x, y, 0, area, 1)  # x, y, z, radius (using area here instead of radius since it needs to be stored somewhere for later), quality
            spot.putFeature('POSITION_T', to_java(float(frame), type='double'))

            spot_collection.add(spot, to_java(frame))
    
    return spot_collection


def create_trackmate_settings(masks):
    image_plus = ij.py.to_imageplus(np.array(masks))

    settings = Settings(image_plus)

    # configure detector (we put nothing here, since we already have the spots)
    settings.detectorFactory = ManualDetectorFactory()
    settings.detectorSettings = {}
    settings.detectorSettings['RADIUS'] = 100.0
    
    # configure tracker
    settings.trackerFactory = SimpleSparseLAPTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
    settings.trackerSettings['LINKING_MAX_DISTANCE'] = 100.0
    settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 10.0
    settings.trackerSettings['MAX_FRAME_GAP'] = to_java(3)
    
    settings.initialSpotFilterValue = -1.0

    return settings


def create_trackmate_model(spots):
    model = Model()
    model.setLogger(Logger.VOID_LOGGER)

    model.setSpots(spots, False)

    return model


def get_track_information(spots):
    start_x = float(spots[0].getDoublePosition(0))
    start_y = float(spots[0].getDoublePosition(1))

    end_x = float(spots[-1].getDoublePosition(0))
    end_y = float(spots[-1].getDoublePosition(1))

    start_area = spots[0].getFeature('RADIUS')  # the area in pixels was passed to the Spot constructor instead of the radius
    end_area = spots[-1].getFeature('RADIUS')

    distance_moved = np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

    angle = get_angle(start_x, start_y, end_x, end_y)
    # slope = (end_y - start_y) / (end_x - start_x)

    return {
        'start_x': start_x,
        'start_y': start_y,
        'end_x': end_x,
        'end_y': end_y,
        'start_area': start_area,
        'end_area': end_area,
        'distance_moved': distance_moved,
        'angle': angle
        # 'slope': slope
    }


def get_angle(start_x, start_y, end_x, end_y):
    angle_radians = np.arctan2(end_y - start_y, end_x - start_x)
    angle_degrees = (180 / np.pi) * angle_radians
    angle_degrees = angle_degrees % 360

    return angle_degrees


def get_results(track_model):
    results = np.empty((0, 8))

    for trackID in track_model.trackIDs(True):
        spots = list(track_model.trackSpots(trackID))

        track_information = get_track_information(spots)

        track_information_numpy = np.array([
            track_information['start_x'],
            track_information['start_y'],
            track_information['end_x'],
            track_information['end_y'],
            track_information['start_area'],
            track_information['end_area'],
            track_information['distance_moved'],
            track_information['angle']
        ])

        results = np.vstack([results, track_information_numpy])  # append the current spot track to the results array
    
    return results


def make_csv(results, file_path):
    sorted_indices = np.argsort(np.abs(results[:, 7] - results[:, 7].mean()))
    results = results[sorted_indices]

    std_in_angle = results[:, 7].std()
    mean_angle = results[:, 7].mean()

    with open(file_path, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['START X', 'START Y', 'END X', 'END Y', 'START AREA', 'END_AREA', 'DISTANCE MOVED', 'ANGLE', 'STANDARD DEVIATIONS AWAY FROM MEAN ANGLE'])

        for row in results:
            writer.writerow([*row, np.abs(row[7] - mean_angle) / std_in_angle])
    
        writer.writerow(['STANDARD DEVIATION IN ANGLE:', std_in_angle])


def make_visualization(masks, results, file_path):
    image = np.zeros((*masks[0].shape, 3), dtype=np.uint8)
    
    before_image = np.where(masks[0].astype(np.uint8) == 0, 0, 255)
    after_image = np.where(masks[1].astype(np.uint8) == 0, 0, 255)

    image[:, :, 0] = before_image
    image[:, :, 2] = after_image

    for result in results:
        cv2.line(image, (int(result[0]), int(result[1])), (int(result[2]), int(result[3])), (0, 255, 0), 2)
    
    cv2.imwrite(str(file_path), image)


def process(experiment_id, csv_path, visualization_path):
    print('Loading images...')
    images = load_experiment_images(experiment_id)

    if images[0].shape != images[1].shape:
        experiments.set_status(experiment_id, -1)

        return

    print('Detecting cells...')
    experiments.increment_status(experiment_id)

    masks = get_masks(images)
    spots = get_spots(masks)

    print('Starting TrackMate...')
    experiments.increment_status(experiment_id)
    trackmate_settings = create_trackmate_settings(masks)
    trackmate_model = create_trackmate_model(spots)

    trackmate = TrackMate(trackmate_model, trackmate_settings)
    trackmate.process()

    track_model = trackmate_model.getTrackModel()

    print('Extracting track results...')
    results = get_results(track_model)

    print('Saving results to csv...')
    make_csv(results, csv_path)

    print('Making visualization...')
    make_visualization(masks, results, visualization_path)

    experiments.increment_status(experiment_id)
