import numpy as np

data_set_x = np.load('inputs.npy')
print(data_set_x)
data_set_y = np.load('outputs.npy')
print('time for y')
print(data_set_y.T)
