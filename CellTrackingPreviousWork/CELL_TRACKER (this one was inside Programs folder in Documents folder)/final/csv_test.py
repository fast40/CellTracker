import csv

def save_track_data(path, track_data, std):
    with open(path, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['STANDARD_DEVIATION_IN_SLOPE:', '])
        writer.writerow(['START_X', 'START_Y', 'END_X', 'END_Y', 'DISTANCE_MOVED', 'DISTANCE_FROM_MEAN'])

        for track in track_data:
            writer.writerow(track)