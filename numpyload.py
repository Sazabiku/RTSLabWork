import numpy as np

data_set_x = np.load('inputs.npy')
data_set_y = np.load('outputs.npy')

word_list = list()
action_list = list()


for item in data_set_x:
    for i in item:
        if i in [0, 1, 2, 3]:
            word_list.append('L')
        if i in [4, 5, 6]:
            word_list.append('M')
        if i in [7, 8, 9, 10]:
            word_list.append('H')


word_list = np.reshape(word_list, (830, 5))


for i in data_set_y:
    if i == 0:
        action_list.append('L')
    if i == 1:
        action_list.append('R')
    if i == 2:
        action_list.append('S')
    if i == 3:
        action_list.append('F')


rules_list = list(zip(action_list, word_list))

print(rules_list)

