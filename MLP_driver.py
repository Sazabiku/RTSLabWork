from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
#import newcar_MLP

data_set_x = np.load('inputs.npy')
data_set_y = np.load('outputs.npy')

#newcar_MLP.run_simulation()

def trainMLP():
    X_train, X_test, y_train, y_test = train_test_split(data_set_x, data_set_y, stratify=data_set_y, random_state=1)
    clf = MLPClassifier(solver='lbfgs', alpha=1e-3, hidden_layer_sizes=(5,), random_state=1).fit(data_set_x, data_set_y) #(X_train, y_train)
    print(X_test)
    print(clf.predict_proba(X_test[:1]))
    print(clf.predict(X_test))
    return clf

if __name__ == "__main__":
    clf = trainMLP()
    print('My pridction is: ', clf.predict([[0, 2, 5, 1, 0]]))