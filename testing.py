from app import test

data = test.run_test()
p1 = data[1]

import numpy as np
grid_x, grid_y = np.mgrid[0:64, 0:64]
points = np.array([[p[0],p[1]] for p in p1])
values = [p[2] for p in p1]
from scipy.interpolate import griddata
grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
import matplotlib.pyplot as plt
plt.plot(points[:,0], points[:,1], 'k.', ms=1)
#plt.plot(grid_z1.T, 'k.', ms=1)
plt.show()