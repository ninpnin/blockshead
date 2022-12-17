import pygame
import random
import numpy as np
from .objects import Direction
from .objects import Pistol, Blood
import math

class Blockshead(object):
    """The Blockshead charecter. Shoot, move, lay mines etc. are all contianed within the Blockshead class. Eventually all of the gun details need to be moved to thier own class so that Pistol = Gun(range,damage) and Mine = Gun(radius, damage)
    eventually even Shotgun = Gun(range,damange,arc_width) and so on"""
    def __init__(self, game_config):
        self.images = {}
        self.images[Direction.UP] = pygame.image.load("images/blockshead/bhup.png") # PhotoImage(file = "images/blockshead/bhup.png") # The image changes if Blockshead is facing up down left right
        self.images[Direction.DOWN] = pygame.image.load("images/blockshead/bhdown.png")
        self.images[Direction.LEFT] = pygame.image.load("images/blockshead/bhleft.png")
        self.images[Direction.RIGHT] = pygame.image.load("images/blockshead/bhright.png")
        self.x = random.randrange(((game_config.width/2)+15),game_config.width) # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.y = random.randrange(0,game_config.height)
        self.direction = Direction.UP
        self.x_vel = 0
        self.y_vel = 0
        self.health = 100 # +5 health is added at the beginning of every level
        self.gun = "Pistol"
        self.ammo = "Infinite"
        self.pause = False
        self.bonus_score = 0
        self.pistol_range = 150 # the range of the pistol in pixels
        self.mine_count = 0 # how many mines are left
        self.bullet_images = []
        self.cooldown = 0
        self.speed = 2.0
    
    def get_image(self):            
        return self.images[self.direction]

    def move(self, game_config):
        # game area boundaries
        if (self.x >= game_config.width) and self.x_vel > 0:
            self.x_vel = 0
        elif self.x <= 0 and self.x_vel < 0:
            self.x_vel = 0

        if (self.y >= game_config.height) and self.y_vel > 0:
            self.y_vel = 0
        elif self.y <= 0 and self.y_vel < 0:
            self.y_vel = 0

        speed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
        if speed < 1.0:
            speed = 1.0
        speed = self.speed / speed
        next_x = self.x + self.x_vel * speed
        next_y = self.y + self.y_vel * speed
        radius = 5
        # TODO: collitions
        
        self.x = next_x
        self.y = next_y
        self.cooldown = max(0, self.cooldown - 1)

    def get_coordinates(self):
        return int(self.x), int(self.y)


class Zombie(object):
    """ZOMBIES. Nothing like a bunch of Zombies that chase you around. Blockshead is faster then Zombies, but Zombies can move diagonally"""
    def __init__(self, window, game_config):
        self.direction = Direction.UP
        self.images = {}
        for direction in Direction:
            # 8 different devil images
            self.images[direction] = pygame.image.load(f"images/zombies/z{direction.name.lower()}.png")

        self.x = random.randrange(0,game_config.width // 3) # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.y = random.randrange(0,game_config.height)

        self.speed = 0.7
        self.health = 50
        self.cooldown = 0
        self.injury_cooldown = 0

    def move(self, target, window, game_config, game_state):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1
            return

        diff_x = self.x - target.x
        if abs(diff_x) < self.speed * 2:
            diff_x = 0
        diff_y = self.y - target.y
        if abs(diff_y) < self.speed * 2:
            diff_y = 0
            
        self.x_vel = - np.sign(diff_x)
        self.y_vel = - np.sign(diff_y)
        self.radius = 25

        speed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
        if speed < 1.0:
            speed = 1.0
        speed = self.speed / speed
        
        next_x = self.x + self.x_vel * speed
        next_y = self.y + self.y_vel * speed

        # TODO: collisions
        
        self.x = next_x
        self.y = next_y
        
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1

    def get_coordinates(self):
        return int(self.x), int(self.y)

    def get_image(self):            
        return self.images[self.direction]
