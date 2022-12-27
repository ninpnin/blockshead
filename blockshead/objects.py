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
        self.width = self.radius
        self.height = self.radius


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
        for zombie in game_state.zombies + game_state.devils:
            cond_x = min_x - self.radius - 2 <= zombie.x <= max_x + self.radius + 2
            cond_y = min_y - self.radius - 2 <= zombie.y <= max_y + self.radius + 2
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

    def draw(self, window, game_state):
        x = min(self.shoot_x_start, self.shoot_x_end)
        width = max(self.shoot_x_start, self.shoot_x_end) - x + 1

        y = min(self.shoot_y_start, self.shoot_y_end)
        height = max(self.shoot_y_start, self.shoot_y_end) - y + 1

        pygame.draw.rect(window, (0,0,0), (x - game_state.offset_x, y - game_state.offset_y, width, height))

class Uzi:
    def __init__(self, game_config, game_state):
        blockshead = game_state.blockshead
        self.direction = blockshead.direction
        x_vel, y_vel = blockshead.direction.value
        self.range = 300
        self.damage = 11
        self.radius = 30
        self.shoot_x_start = x_vel * (blockshead.radius - 5) + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1 + y_vel * ( random.random() - 0.5) * 25
        self.shoot_y_start = y_vel * (blockshead.radius - 5) + blockshead.y
        self.shoot_y_end = y_vel * self.range + blockshead.y + 1 + x_vel * ( random.random() - 0.5) * 25
        self.lifetime = 3

        self.attacked = False
        mixer.music.load('audio/uzi.mp3')
        mixer.music.play()

    def contact(self, game_state):
        killed_zombies, killed_devils = [], []

        max_x, min_x = max(self.shoot_x_start, self.shoot_x_end), min(self.shoot_x_start, self.shoot_x_end)
        max_y, min_y = max(self.shoot_y_start, self.shoot_y_end), min(self.shoot_y_start, self.shoot_y_end)
        
        # Calculate damage inflicted on regular zombies
        killed_zombies = []
        for zombie in game_state.zombies + game_state.devils:
            cond_x = min_x - self.radius - 2 <= zombie.x <= max_x + self.radius + 2
            cond_y = min_y - self.radius - 2 <= zombie.y <= max_y + self.radius + 2
            if cond_x and cond_y:
                zombie.injure(self.damage, game_state)

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        self.lifetime -= 1

        if not self.attacked:
            self.attacked = True
            return self.contact(game_state)

        return [], []

    def draw(self, window, game_state):
        start = self.shoot_x_start - game_state.offset_x, self.shoot_y_start  - game_state.offset_y
        end = self.shoot_x_end - game_state.offset_x, self.shoot_y_end  - game_state.offset_y
        pygame.draw.line(window, (200,190,170), start, end)
        #pygame.draw.rect(window, (0,0,0), (x - game_state.offset_x, y - game_state.offset_y, width, height))

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
        for zombie in game_state.zombies + game_state.devils:
            diff = np.array([zombie.x - self.shoot_x_start, zombie.y - self.shoot_y_start])
            distance = np.linalg.norm(diff)
            cosine = np.dot(diff / np.linalg.norm(diff), self.direction)
            min_cos = np.cos(np.radians(self.angle))
            if distance <= self.range and cosine >= min_cos:
                zombie.injure(self.damage, game_state)

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

    def draw(self, window, game_state):
        for angle in [0, self.angle, -self.angle]:
            theta = np.radians(angle + random.uniform(-10, 10))
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))

            x = np.array([self.shoot_x_end - self.shoot_x_start, self.shoot_y_end - self.shoot_y_start])
            x_prime = R @ x
            x_end, y_end = int(x_prime[0]) + self.shoot_x_start, int(x_prime[1]) + self.shoot_y_start
            start = self.shoot_x_start - game_state.offset_x, self.shoot_y_start  - game_state.offset_y
            end = x_end - game_state.offset_x, y_end  - game_state.offset_y
            pygame.draw.line(window, (200,190,170), start, end)

class DevilAttack:
    def __init__(self, devil, game_state):
        self.speed = 3.5
        self.devil = devil
        blockshead = game_state.blockshead
        self.direction = np.array([blockshead.x - devil.x, blockshead.y - devil.y])
        self.direction = self.direction / np.linalg.norm(self.direction) * self.speed

        self.image = pygame.image.load("images/game_elements/devil_a_old.png")
        self.radius = 30
        initial_step = self.direction * (self.radius / 2) / self.speed
        self.x = devil.x + initial_step[0]
        self.y = devil.y + initial_step[1]
        self.damage = 30
        self.lifetime = 80

        self.attacked = False
        #mixer.music.load('audio/uzi.mp3')
        #mixer.music.play()

    def contact(self, game_state):
        hit = False
        for zombie in game_state.zombies + game_state.devils + [game_state.blockshead]:
            if zombie == self.devil:
                continue
            diff_x = zombie.x - self.x
            diff_y = zombie.y - self.y
            if np.sqrt(diff_x ** 2 + diff_y ** 2) <= self.radius:
                zombie.injure(self.damage, game_state)
                hit = True

        return hit

    def update(self, game_config, game_state):
        self.lifetime -= 1

        self.x += self.direction[0]
        self.y += self.direction[1]

        if not self.attacked:
            self.attacked = self.contact(game_state)
        else:
            self.lifetime = -1

        return [], []

    def draw(self, window, game_state):
        x = self.x - self.image.get_width() // 2
        y = self.y - self.image.get_height() // 2
        window.blit(self.image, (x,y))

class Healthbox(object):
    """Static object for drawing blood on the ground"""
    def __init__(self, game_state, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/game_elements/healthbox.png")
        self.radius = 25
        self.width = self.radius
        self.height = self.radius

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
                game_state.messages.append((f"Regained health", 180))
            else:
                print(f"Picked up {self.type}")
                game_state.messages.append((f"Picked up {self.type}", 180))
                # Increment ammo of self.type 2/3 of max ammo, cap at max ammo
                max_ammo = game_state.max_ammo[self.type]
                game_state.blockshead.ammo_dict[self.type] += 2 * max_ammo // 3
                game_state.blockshead.ammo_dict[self.type] = min(max_ammo, game_state.blockshead.ammo_dict[self.type])
            self.active = False
            newlevel_audio = pygame.mixer.Sound('audio/healthbox.mp3')
            mixer.Channel(2).play(newlevel_audio)


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
        self.width = self.radius
        self.height = self.radius
        
    def get_image(self):
        return self.image

    def get_coordinates(self):
        return self.x, self.y
