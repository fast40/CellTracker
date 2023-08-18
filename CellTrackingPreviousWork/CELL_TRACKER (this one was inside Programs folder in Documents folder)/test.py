from cellpose import models
from time import time

t1 = time()

model = models.Cellpose(gpu=True, model_type='cyto2')

t2 = time()

print(t2 - t1)