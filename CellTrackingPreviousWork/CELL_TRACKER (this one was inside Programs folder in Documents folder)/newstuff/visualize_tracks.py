from track_cells import main
import cv2
import numpy as np


model, masks = main(gpu=True)
track_model = model.getTrackModel()


shape = masks[0].shape

image1_base = np.zeros((*shape, 3), dtype=np.uint8)
image2_base = np.zeros((*shape, 3), dtype=np.uint8)

image1 = masks[0].astype(np.uint8)
image2 = masks[1].astype(np.uint8)

image1 = np.where(image1 == 0, 0, 200)
image2 = np.where(image2 == 0, 0, 200)

image1_base[:, :, 2] = image1
image2_base[:, :, 0] = image2

image = cv2.add(image1_base, image2_base)

print(image.shape)
# image = np.expand_dims(image, axis=2)
# image = image.repeat(3, axis=2)


distances = []

for trackID in track_model.trackIDs(True):
    spots = track_model.trackSpots(trackID)
    spots = list(spots)

    for spot in range(1, len(spots)):
        spot1 = spots[spot - 1]
        spot2 = spots[spot]

        x1 = int(spot1.getDoublePosition(0))
        y1 = int(spot1.getDoublePosition(1))

        x2 = int(spot2.getDoublePosition(0))
        y2 = int(spot2.getDoublePosition(1))

        distance = ((y2-y1)**2 + (x2-x1)**2)**0.5

        distances.append(distance)

        # cv2.line(image, (x1, y1), (x2, y2), (0, 255, 255), thickness=3)
        cv2.line(image, (x1, y1), (x2, y2), (0, 200, 0), 2)
    
for distance in distances:
    print(distance)

print(f'Max distance: {max(distances)}')


# image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))

cv2.imwrite('/home/elifast/Documents/Programs/CELL_TRACKER/newstuff/output2.png', image)

cv2.imshow('image', image)

cv2.waitKey(0)
cv2.destroyAllWindows()




