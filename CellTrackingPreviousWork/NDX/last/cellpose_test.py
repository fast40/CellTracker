# import imagej
# import scyjava
from cellpose import models, io
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# ij = imagej.init('/opt/Fiji.app')

# TrackMate = scyjava.jimport('fiji.plugin.trackmate.TrackMate')
# tm = TrackMate()
 
# model = models.Cellpose(gpu=True, model_type='cyto2')





channels = [0, 0]

filename = 'after.tif'

img = io.imread(filename)
img2 = Image.open('examples/image-after.png').convert('L').convert('L')

print(np.array_equal(img, img2))

print(img[0][:10])
print(np.array(img2)[0][:10])










# masks, flows, styles, diams = model.eval(img, diameter=None, channels=channels)

# print(type(flows[0]))

# # save results so you can load in gui
# io.masks_flows_to_seg(img, masks, flows, diams, filename, channels)

# # save results as png
# io.save_to_png(img, masks, flows, filename)









# # DISPLAY RESULTS
# from cellpose import plot

# fig = plt.figure(figsize=(12,5))

# plot.show_segmentation(fig, img, masks, flows[0], channels=channels)
# plt.tight_layout()
# plt.show()