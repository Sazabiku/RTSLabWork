from sklearn.neural_network import MLPClassifier
import numpy as np
#import newcar_MLP

data_set_x = np.load('inputs.npy')
data_set_y = np.load('outputs.npy')

#newcar_MLP.run_simulation()