from detect import run_cellpose
import numpy as np


masks = run_cellpose(gpu=True)['0']
print(masks[0].dtype)  # uint16

np.save('masks.npy', masks)