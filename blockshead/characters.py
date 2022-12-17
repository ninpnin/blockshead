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

    def _check_collisions(self, x, y, game_state, radius=40):
        for zombie in game_state.zombies:
            dist = math.sqrt((zombie.x - x)**2 + (zombie.y - y)**2)
            if dist < radius:
                return True
        return False

    def move(self, game_config, game_state):
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
        
        if not self._check_collisions(next_x, next_y, game_state):
            self.x = next_x
            self.y = next_y

        self.cooldown = max(0, self.cooldown - 1)

    def get_coordinates(self):
        return int(self.x), int(self.y)

    def fire_gun(self, window, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        self.bonus_score = 0
        if self.cooldown == 0:
            if self.gun == "Pistol":
                shot = Pistol(game_config, game_state)
                self.cooldown = 20
                game_state.shots.append(shot)
            elif self.gun == "Uzi":
                if game_state.blockshead.ammo > 0:
                    #shot = Uzi(game_config, game_state)
                    self.cooldown = 10
                    game_state.shots.append(shot)
            elif self.gun == "Fireball":
                if game_state.blockshead.ammo > 0:
                    #shot = Fireball(window, game_config, game_state)
                    self.cooldown = 30
                    game_state.shots.append(shot)

class Zombie(object):
    def __init__(self, window, game_config):
        self.direction = Direction.UP
        self.images = {}
        for direction in Direction:
            # 8 different devil images
            self.images[direction] = pygame.image.load(f"images/zombies/z{direction.name.lower()}.png")

        # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.x = random.randrange(0,game_config.width // 3)
        self.y = random.randrange(0,game_config.height)

        self.speed = 0.7
        self.health = 50
        self.cooldown = 0
        self.injury_cooldown = 0
        self.radius = 50
    
    def _check_collisions(self, x, y, game_state, radius=40):
        for zombie in game_state.zombies + [game_state.blockshead]:
            if zombie is self:
                continue
            dist = math.sqrt((zombie.x - x)**2 + (zombie.y - y)**2)
            if dist < radius:
                return True
        return False

    def move(self, window, game_config, game_state):
        target = game_state.blockshead
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1
            return

        diff = np.array([self.x - target.x, self.y - target.y])
        diff = diff / np.linalg.norm(diff) * self.speed
        
        for angle in [0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150]:
            theta = np.radians(angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            direction = R @ diff
            next_x = self.x - direction[0]
            next_y = self.y - direction[1]

            collisions = self._check_collisions(next_x, next_y, game_state)
            if not collisions:
                break
            
        self.x = next_x
        self.y = next_y
        
        # Cooldown period for shooting
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.injury_cooldown > 0:
            self.injury_cooldown -= 1

    def get_coordinates(self):
        return int(self.x), int(self.y)

    def get_image(self):            
        return self.images[self.direction]

    def contact(self, game_state):
        target = game_state.blockshead
        if abs(target.x - self.x) < self.radius + 2 and abs(target.y - self.y) < self.radius + 2 and self.cooldown == 0:
            target.health -= 1
            self.cooldown = 5
            print(target.health)
