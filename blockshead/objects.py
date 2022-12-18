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
        self.radius = 30

    def get_coordinates(self):
        return int(self.x), int(self.y)
    
    def get_image(self):
        return self.image
    
    def levelup(self):
        self.level_lifetime -= 1

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
        self.shoot_x_start = x_vel * 5 + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1
        self.shoot_y_start = y_vel * 5 + blockshead.y
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

    def draw(self, window):
        x = min(self.shoot_x_start, self.shoot_x_end)
        width = max(self.shoot_x_start, self.shoot_x_end) - x + 1

        y = min(self.shoot_y_start, self.shoot_y_end)
        height = max(self.shoot_y_start, self.shoot_y_end) - y + 1

        pygame.draw.rect(window, (0,0,0), (x, y, width, height))

class Uzi:
    def __init__(self, game_config, game_state):
        blockshead = game_state.blockshead
        self.direction = blockshead.direction
        x_vel, y_vel = blockshead.direction.value
        self.range = 250
        self.damage = 11
        self.radius = 30
        self.shoot_x_start = x_vel * 5 + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1
        self.shoot_y_start = y_vel * 5 + blockshead.y
        self.shoot_y_end = y_vel * self.range + blockshead.y + 1
        self.lifetime = 3

        self.attacked = False
        mixer.music.load('audio/uzi.wav')
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

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        self.lifetime -= 1

        # Update image width
        self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2

        if not self.attacked:
            self.attacked = True
            return self.contact(game_state)

        return [], []

    def draw(self, window):
        x = min(self.shoot_x_start, self.shoot_x_end)
        width = max(self.shoot_x_start, self.shoot_x_end) - x + 1

        y = min(self.shoot_y_start, self.shoot_y_end)
        height = max(self.shoot_y_start, self.shoot_y_end) - y + 1

        pygame.draw.rect(window, (0,0,0), (x, y, width, height))

class Shotgun:
    def __init__(self, game_config, game_state):
        blockshead = game_state.blockshead
        self.direction = blockshead.direction
        x_vel, y_vel = self.direction.value
        self.direction = np.array(self.direction.value) / np.linalg.norm(self.direction.value)
        self.range = 200
        self.angle = 19
        self.damage = 20
        self.radius = 30
        self.shoot_x_start = x_vel * 5 + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1
        self.shoot_y_start = y_vel * 5 + blockshead.y
        self.shoot_y_end = y_vel * self.range + blockshead.y + 1
        self.lifetime = 3

        self.attacked = False
        mixer.music.load('audio/shotgun.wav')
        mixer.music.play()

    def contact(self, game_state):
        killed_zombies, killed_devils = [], []

        # Does damage if distance <= max distance and angle < max angle
        injured = 0
        for zombie in game_state.zombies:
            diff = np.array([zombie.x - self.shoot_x_start, zombie.y - self.shoot_y_start])
            distance = np.linalg.norm(diff)
            cosine = np.dot(diff / np.linalg.norm(diff), self.direction)
            min_cos = np.cos(np.radians(self.angle))
            if distance <= self.range and cosine >= min_cos:
                zombie.injure(self.damage, game_state)
                injured += 1
                
        if injured >= 1:
            print("injured", injured)

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        self.lifetime -= 1

        # Update image width
        #self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        #self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2

        if not self.attacked:
            self.attacked = True
            return self.contact(game_state)

        return [], []

    def draw(self, window):
        for angle in [0, self.angle, -self.angle]:
            theta = np.radians(angle + random.uniform(-10, 10))
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))

            x = np.array([self.shoot_x_end - self.shoot_x_start, self.shoot_y_end - self.shoot_y_start])
            x_prime = R @ x
            x_end, y_end = int(x_prime[0]) + self.shoot_x_start, int(x_prime[1]) + self.shoot_y_start
            pygame.draw.line(window, (0,0,0), (self.shoot_x_start, self.shoot_y_start), (x_end, y_end))


class Healthbox(object):
    """Static object for drawing blood on the ground"""
    def __init__(self, game_config, game_state):
        self.x = random.randrange(0, game_config.width) # create Zombies in the left half of the arena
        self.y = random.randrange(0, game_config.height)
        self.image = pygame.image.load("images/game_elements/healthbox.png")
        self.radius = 25
        types = ["health"]
        available_weapons = [w for w in game_state.available_weapons if w != "pistol"]
        if len(available_weapons) > 1:
            types += ["ammo"]
        self.type = random.choice(types)
        if self.type == "ammo":
            self.type = random.choice(available_weapons)
        self.health = 50
        self.active = True

    def update(self, game_config, game_state):
        diff_x = abs(game_state.blockshead.x - self.x)
        diff_y = abs(game_state.blockshead.y - self.y)
        if diff_x < self.radius and diff_y < self.radius:
            if self.type == "health":
                game_state.blockshead.health = game_state.blockshead.health + self.health
                game_state.blockshead.health = min(game_config.max_health, game_state.blockshead.health)
            else:
                print(f"Picked up {self.type}")
                # Increment ammo of self.type 2/3 of max ammo, cap at max ammo
                max_ammo = game_config.ammo[self.type]
                game_state.blockshead.ammo_dict[self.type] += 2 * max_ammo // 3
                game_state.blockshead.ammo_dict[self.type] = min(max_ammo, game_state.blockshead.ammo_dict[self.type])
            self.active = False

    def get_image(self):
        return self.image

    def get_coordinates(self):
        return self.x, self.y


class Fakewall(object):
    def __init__(self, game_config):
        self.x = random.randrange(0, game_config.width)
        self.y = random.randrange(0, game_config.height)
        self.image = pygame.image.load("images/game_elements/fakewall80.png")
        self.radius = 35
        
    def get_image(self):
        return self.image

    def get_coordinates(self):
        return self.x, self.y
