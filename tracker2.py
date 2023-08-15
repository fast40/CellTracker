import numpy as np


def get_spots(masks):
    spot_collection = SpotCollection()

    for frame, mask in enumerate(masks):  # iterate over each frame
        for cell in range(1, mask.max() + 1):  # iterate over each cell in the mask
            coords = np.where(mask == cell)
    
            area = len(coords[0])

            radius = np.sqrt(area / np.pi)
            radius = radius.round()
            radius = radius.astype(int)

            center = np.mean(coords, axis=1)
            center = center.round()
            center = center.astype(int)

            y, x = center

            spot = Spot(x, y, 0, radius, 1)  # x, y, z, radius, quality
            spot.putFeature('POSITION_T', to_java(float(frame), type='double'))

            spot_collection.add(spot, to_java(frame))
    
    return spot_collection
