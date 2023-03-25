import copy
from matplotlib import pyplot as plt
plt.rc("figure", figsize=(10, 10))

from fuzzylogic.classes import Domain, Set, Rule
from fuzzylogic.hedges import very
from fuzzylogic.functions import (sigmoid, gauss, trapezoid, triangular_sigmoid, rectangular, singleton)

class Fuzzy_Driver:

    def __init__(self):
        ## 
        right_sensor = Domain('Right', 0, 300)
        right_sensor.VL = gauss(0, 0.00025)
        right_sensor.L = gauss(100, 0.00025)
        right_sensor.M = gauss(200, 0.00025)
        right_sensor.H = gauss(300, 0.00025)

        # right_sensor.VL.plot()
        # right_sensor.L.plot()
        # right_sensor.M.plot()
        # right_sensor.H.plot()
        # plt.show()

        ## 
        right_straight_sensor = Domain('Right_Straight', 0, 300)
        right_straight_sensor.VL = gauss(0, 0.00025)
        right_straight_sensor.L = gauss(100, 0.00025)
        right_straight_sensor.M = gauss(200, 0.00025)
        right_straight_sensor.H = gauss(300, 0.00025)

        ##
        straight_sensor = Domain('Straight', 0, 300)
        straight_sensor.VL = gauss(0, 0.00025)
        straight_sensor.L = gauss(100, 0.00025)
        straight_sensor.M = gauss(200, 0.00025)
        straight_sensor.H = gauss(300, 0.00025)

        ##
        left_straight_sensor = Domain('Left_Straight', 0, 300)
        left_straight_sensor.VL = gauss(0, 0.00025)
        left_straight_sensor.L = gauss(100, 0.00025)
        left_straight_sensor.M = gauss(200, 0.00025)
        left_straight_sensor.H = gauss(300, 0.00025)

        ##
        left_sensor = Domain('Left', 0, 300)
        left_sensor.VL = gauss(0, 0.00025)
        left_sensor.L = gauss(100, 0.00025)
        left_sensor.M = gauss(200, 0.00025)
        left_sensor.H = gauss(300, 0.00025)


        ##
        action = Domain('Action', 0, 5)
        action.L = singleton(1)
        action.R = singleton(2)
        action.S = singleton(3)
        action.F = singleton(4)

        # action.L.plot()
        # action.R.plot()
        # action.S.plot()
        # action.F.plot()
        # plt.show()

        R1 = Rule({(right_sensor.VL, right_straight_sensor.VL, straight_sensor.VL, left_straight_sensor.VL, left_sensor.VL): action.L})
        R2 = Rule({(right_sensor.L, right_straight_sensor.VL): action.L})
        R3 = Rule({(right_sensor.L, right_straight_sensor.L): action.L})

        R4 = Rule({(left_sensor.VL, left_straight_sensor.VL): action.R})
        R5 = Rule({(left_sensor.L, left_straight_sensor.VL): action.R})
        R6 = Rule({(left_sensor.L, left_straight_sensor.L): action.R})

        self.rules = sum([R1, R2, R3, R4, R5, R6])
        
        def get_action(self, car):
            radars = car.get_not_normal_data()
            
            values = {  right_sensor: radars[0], 
                        right_straight_sensor: radars[1], 
                        straight_sensor: radars[2], 
                        left_straight_sensor: radars[3], 
                        left_sensor: radars[4],
                     }
                     
            return int(math.round(rules(values)))

