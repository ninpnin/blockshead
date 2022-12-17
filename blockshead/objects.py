import numpy as np
import random
import pygame
from pygame import mixer
from enum import Enum

class Direction(Enum):
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    
    LEFTUP =    (-1,-1)
    LEFTDOWN =  (-1, 1)
    RIGHTUP =   (1, -1)
    RIGHTDOWN = (1,  1)

class Blood(object):
    """Static object for drawing blood on the ground"""
    def __init__(self, x,y):
        self.image = pygame.image.load("images/game_elements/blood.gif")
        self.level_lifetime = 2
        self.x = x
        self.y = y

    def get_coordinates(self):
        return int(self.x), int(self.y)
    
    def get_image(self):
        return self.image
    """
    def levelup(self, game_config, game_state):
        self.level_lifetime -= 1
        if self.level_lifetime <= 0:
            game_config.canvas.delete(self.image)
            game_state.blood_marks.remove(self)
    """

"""
Weapons. These classes depict shots coming from the weapons.
"""
class Pistol:
    def __init__(self, game_config, game_state):
        canvas = game_config.canvas
        blockshead = game_state.blockshead
        self.direction = blockshead.direction
        x_vel, y_vel = blockshead.direction.value
        self.range = 100
        self.damage = 11
        self.radius = 30
        self.shoot_x_start = x_vel * 10 + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1
        self.shoot_y_start = y_vel * 10 + blockshead.y
        self.shoot_y_end = y_vel * self.range + blockshead.y + 1
        self.lifetime = 3
        self.attacked = False

        mixer.music.load('audio/pistol.mp3')
        mixer.music.play()

    def contact(self, game_state):
        killed_zombies, killed_devils = [], []

        max_x, min_x = max(self.shoot_x_start, self.shoot_x_end), min(self.shoot_x_start, self.shoot_x_end)
        max_y, min_y = max(self.shoot_y_start, self.shoot_y_end), min(self.shoot_y_start, self.shoot_y_end)
        
        # Calculate damage inflicted on regular zombies
        killed_zombies = []
        for zombie in game_state.zombies:
            cond_x = min_x - self.radius <= zombie.x <= max_x + self.radius
            cond_y = min_y - self.radius <= zombie.y <= max_y + self.radius
            if cond_x and cond_y:
                zombie.injure(self.damage, game_state)
                killed_zombies.append(zombie)

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        self.lifetime -= 1

        # Update image width
        self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2
        
        # TODO: draw shot
        
        if not self.attacked:
            self.attacked = True
            return self.contact(game_state)

        return [], []

