# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# Code Changed By: Alexey Vulfin, Nikolai Baturov

import copy
from matplotlib import pyplot as plt
plt.rc("figure", figsize=(10, 10))

import numpy as np


import math
import random
import sys
import os

import neat
import pygame

from win32api import GetSystemMetrics
import ctypes

from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

ctypes.windll.user32.SetProcessDPIAware()

# Constants
# WIDTH = 1600
# HEIGHT = 880


WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)


CAR_SIZE_X = 60    
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255) # Color To Crash on Hit

current_generation = 0 # Generation counter

#Arrays_of_radars = list()
#Arrays_of_choices = list()

data_set_x = np.load('inputs.npy')
data_set_y = np.load('outputs.npy')



class MLP_driver:

    def trainMLP():
        X_train, X_test, y_train, y_test = train_test_split(data_set_x, data_set_y, stratify=data_set_y, random_state=1)
        clf = MLPClassifier(solver='lbfgs', alpha=1e-3, hidden_layer_sizes=(5,), random_state=1).fit(data_set_x, data_set_y) #(X_train, y_train)
        #print(X_test)
        print(clf.predict_proba(X_test[:1]))
        #print(clf.predict(X_test))
        return clf
    


class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('FPV.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # self.position = [690, 740] # Starting Position
        self.position = [330, 940] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 600:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 14
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            #print(radar)
            return_values[i] = int(radar[1] / 30)
        print(return_values)
        #Arrays_of_radars.append(return_values)
        #with open('test.npy', 'wb') as f:
            #np.save(f, np.array(return_values))

        return return_values
        
    def get_not_normal_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = radar[1]

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image
    
    def get_posi(self):
        return self.position


def run_simulation():

    MLP_CLF = MLP_driver.trainMLP()
    
    # Empty Collections For Cars
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    # screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    gui_font = pygame.font.SysFont("Arial", 30)

    class Button:
        def __init__(self,text,width,height,pos,elevation):
            #Core attributes 
            self.pressed = False
            self.elevation = elevation
            self.dynamic_elecation = elevation
            self.original_y_pos = pos[1]

            # top rectangle 
            self.top_rect = pygame.Rect(pos,(width,height))
            self.top_color = '#567BED'

            # bottom rectangle 
            self.bottom_rect = pygame.Rect(pos,(width,height))
            self.bottom_color = '#354B5E'
            #text
            self.text_surf = gui_font.render(text, True, '#171210')
            self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

        def draw(self):
            # elevation logic 
            self.top_rect.y = self.original_y_pos - self.dynamic_elecation
            self.text_rect.center = self.top_rect.center 

            self.bottom_rect.midtop = self.top_rect.midtop
            self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

            pygame.draw.rect(game_map,self.bottom_color, self.bottom_rect,border_radius = 12)
            pygame.draw.rect(game_map,self.top_color, self.top_rect,border_radius = 12)
            #pygame.draw.rect(game_map,self.top_color, self.text_rect,border_radius = 12)
            game_map.blit(self.text_surf, self.text_rect)
            self.check_click()

        def check_click(self):
            mouse_pos = pygame.mouse.get_pos()
            if self.top_rect.collidepoint(mouse_pos):
                self.top_color = '#D74B4B'
                if pygame.mouse.get_pressed()[0]:
                    self.dynamic_elecation = 0
                    self.pressed = True
                else:
                    self.dynamic_elecation = self.elevation
                    if self.pressed == True:
                        print('clicked')
                        self.pressed = False
            else:
                self.dynamic_elecation = self.elevation
                self.top_color = '#567BED'


    cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 24)
    game_map = pygame.image.load('mapNEW.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)

    wind_speed = 4

    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 5000)
    timer_event_2 = pygame.USEREVENT + 2
    pygame.time.set_timer(timer_event_2, 8000)

    button1 = Button('LEFT',80,80,(30,600),5)
    button2 = Button('RIGHT',80,80,(30,900),5)
    button3 = Button('UP',80,80,(1820,600),5)
    button4 = Button('DOWN',80,80,(1820,900),5)
    button5 = Button('Запустить новый БПЛА (Y)',320,80,(1400,200),5)
    button6 = Button('Потеря связи (L)',220,80,(200,200),5)
    button7 = Button('ВЫХОД (ESC)',200,80,(30,30),5)


    while True:
        button1.draw()
        button2.draw()
        button3.draw()
        button4.draw()
        button5.draw()
        button6.draw()
        button7.draw()
        link_flag = True
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == timer_event:
                if (wind_speed + np.random.randint(-1, 1) >= 0):
                    wind_speed = wind_speed + np.random.randint(-1, 1)
                if (wind_speed + np.random.randint(-1, 1) < 0):
                    wind_speed = 0
                if wind_speed >= 4:
                    if(car.speed - wind_speed >= 5):
                        car.speed = car.speed - wind_speed + 4
                if wind_speed < 4:
                    if(car.speed - wind_speed <= 25):
                        car.speed = car.speed + wind_speed
            if event.type == timer_event_2:
                flag = np.random.randint(0, 1)
                if flag == 1:
                    link_flag = not(link_flag)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = MLP_CLF.predict([car.get_data()])
            choice = max(output)
            print(choice)
            #print(output)
            #print(choice)
            
            #aid = Fuzzy_Driver()
            #print(aid.get_action(car))
            
            #Добавлено ручное управление
            keys = pygame.key.get_pressed()
            #choice = 0
            if keys[pygame.K_LEFT]:
                choice = 0
            if keys[pygame.K_RIGHT]:
                choice = 1
            if keys[pygame.K_DOWN]:
                choice = 2
            if keys[pygame.K_UP]:
                choice = 3
            if button1.pressed:
                choice = 0
            if button2.pressed:
                choice = 1
            if button3.pressed:
                choice = 3
            if button4.pressed:
                choice = 2 

            if button6.pressed:
                link_flag = not(link_flag)
            if keys[pygame.K_l]:
                link_flag = not(link_flag)

            if link_flag == False:
                if keys[pygame.K_LEFT]:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if keys[pygame.K_RIGHT]:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if keys[pygame.K_DOWN]:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if keys[pygame.K_UP]:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if button1.pressed:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if button2.pressed:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if button3.pressed:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                if button4.pressed:
                    output = MLP_CLF.predict([car.get_data()])
                    choice = max(output)
                text = generation_font.render("СВЯЗЬ ПОТЕРЯНА", True, (255,0,0))
                text_rect = text.get_rect()
                text_rect.center = (990, 90)
                pygame.draw.rect(game_map, (255, 255, 255), pygame.Rect((850, 50), (260, 70))) 
                game_map.blit(text, text_rect) 
            if link_flag == True:
                text = generation_font.render("СВЯЗЬ ЕСТЬ", True, (0,255,0))
                text_rect = text.get_rect()
                text_rect.center = (990, 90)
                pygame.draw.rect(game_map, (255, 255, 255), pygame.Rect((850, 50), (260, 70))) 
                game_map.blit(text, text_rect)

            print(choice)
            print(link_flag)
            #Arrays_of_choices.append(choice)
            
                         
            if choice == 0:
                car.angle += 10 # Left
            elif choice == 1:
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 1 >= 10):
                    car.speed -= 1 # Slow Down
            elif choice == 3:
                if(car.speed + 1 <= 25):
                    car.speed += 1 # Speed Up


        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)

        if keys[pygame.K_ESCAPE]:
            break
        if button7.pressed:
            break

        if keys[pygame.K_y]:
            run_simulation()
        if button5.pressed:
            run_simulation()

        if still_alive == 0:
            #print(Arrays_of_radars)
            #with open('inputs.npy', 'wb') as f:
                #np.save(f, np.array(Arrays_of_radars))
            #with open('outputs.npy', 'wb') as f:
                #np.save(f, np.array(Arrays_of_choices))
            print('bye...')
            text = generation_font.render("СВЯЗЬ ПОТЕРЯНА", True, (255,0,0))
            text_rect = text.get_rect()
            text_rect.center = (990, 90)
            pygame.draw.rect(game_map, (255, 255, 255), pygame.Rect((850, 50), (260, 70))) 
            game_map.blit(text, text_rect) 

            

        #counter += 1
        #if counter == 30 * 40: # Stop After About 20 Seconds
            #break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # Display Info
        text = alive_font.render("Направление: ", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (70, 500)
        screen.blit(text, text_rect)
        text = alive_font.render("Влево", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (70, 700)
        screen.blit(text, text_rect)
        text = alive_font.render("Вправо", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (70, 1000)
        screen.blit(text, text_rect)
        text = alive_font.render("Скорость: ", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (1850, 500)
        screen.blit(text, text_rect)
        text = alive_font.render("Выше", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (1857, 700)
        screen.blit(text, text_rect)
        text = alive_font.render("Ниже", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (1857, 1000)
        screen.blit(text, text_rect)
        text = generation_font.render("ИВТ-324Б Батуров Н.В.", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (990, 30)
        screen.blit(text, text_rect)
        text = generation_font.render("Скорость БПЛА: " + str(car.speed) + ' m/s', True, (0,20,200))
        text_rect = text.get_rect()
        text_rect.center = (990, 350)
        screen.blit(text, text_rect)
        text = generation_font.render("Скорость Ветра: " + str(wind_speed) + ' m/s', True, (255,50,50))
        text_rect = text.get_rect()
        text_rect.center = (990, 380)
        screen.blit(text, text_rect)

        text = generation_font.render("Позиция БПЛА: " + 'X: ' + str(round(car.get_posi()[0])) + ' Y: ' + str(round(car.get_posi()[1])), True, (10, 255, 10))
        text_rect = text.get_rect()
        text_rect.center = (990, 320)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(20) # ХХ FPS

if __name__ == "__main__":
    
    run_simulation()
