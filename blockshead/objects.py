import numpy as np
import tkinter as tk
from tkinter import *
import random
import time
import math
from enum import Enum
from playsound import playsound

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
    def __init__(self,x,y, game_config):
        self.image = PhotoImage(file = "images/game_elements/blood.png")
        self.blood_spot = game_config.canvas.create_image(x,y,image = self.image)
        game_config.canvas.tag_lower(self.blood_spot)
        game_config.canvas.tag_lower(game_config.background)

class DevilAttack(object):
    """The yellow circle that the devils use to attack Blockshead. It has a life span of 125 timesteps.
    Is also deleted upon hitting Blockshead"""
    def __init__(self, x, y, x_vel, y_vel, canvas):
        self.x = x
        self.y = y
        self.image = PhotoImage(file = "images/game_elements/devil_a_old.png")
        self.attack = canvas.create_image(self.x,self.y,image = self.image)
        self.x_vel = x_vel
        if self.x_vel > 0: # If the velocity in that direction is not 0 it adds 1 to the speed so that it is faster than the Devil who shot it.
            self.x_vel += .75
        if self.x_vel < 0:
            self.x_vel -= .75
        self.y_vel = y_vel
        if self.y_vel > 0:
            self.y_vel += .75
        if self.y_vel < 0:
            self.y_vel -= .75
        self.life_span = 125

        if self.x_vel == 0 or self.y_vel == 0:
            self.x_vel, self.y_vel = self.x_vel * 2, self.y_vel * 2
        else:
            self.x_vel, self.y_vel = self.x_vel * 1.41, self.y_vel * 1.41
    def move(self, canvas, target):
        self.x += self.x_vel
        self.y += self.y_vel
        canvas.coords(self.attack,self.x,self.y)
        self.life_span -=1
        if abs(self.x - target.x) < 30 and abs(self.y - target.y) < 30: #Strike Blockshead if within 30 pixels
            target.health -= 10
            self.life_span = 0

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
        self.image = canvas.create_rectangle(self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end,fill="Red") # create the bullet

        self.attacked = False

        playsound('audio/pistol.mp3', False)

    def contact(self, game_config, game_state):
        killed_zombies, killed_devils = [], []

        max_x, min_x = max(self.shoot_x_start, self.shoot_x_end), min(self.shoot_x_start, self.shoot_x_end)
        max_y, min_y = max(self.shoot_y_start, self.shoot_y_end), min(self.shoot_y_start, self.shoot_y_end)
        
        # Calculate damage inflicted on regular zombies
        for zombie_ix, Zombie in game_state.Zombie_Dict.items():
            cond_x = min_x - self.radius <= Zombie.x <= max_x + self.radius
            cond_y = min_y - self.radius <= Zombie.y <= max_y + self.radius
            if cond_x and cond_y:
                Zombie.injure(self.damage)
                killed_zombies.append(zombie_ix)

        # Calculate damage inflicted on devils
        for devil_ix, Zombie in game_state.Devil_Dict.items():
            cond_x = min_x - self.radius <= Zombie.x <= max_x + self.radius
            cond_y = min_y - self.radius <= Zombie.y <= max_y + self.radius

            if cond_x and cond_y:
                Zombie.injure(self.damage) # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                killed_devils.append(devil_ix)

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        canvas = game_config.canvas
        if self.lifetime < 0:
            canvas.delete(self.image)
            canvas.update()
            game_state.shots.remove(self)
            return [], []

        self.lifetime -= 1

        # Update image width
        self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2
        canvas.coords(self.image, self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end)
        canvas.update()

        if not self.attacked:
            self.attacked = True
            return self.contact(game_config, game_state)

        return [], []



class Uzi:
    def __init__(self, game_config, game_state):
        canvas = game_config.canvas
        blockshead = game_state.blockshead
        self.direction = blockshead.direction
        x_vel, y_vel = blockshead.direction.value
        self.range = 250
        self.damage = 11
        self.radius = 30
        self.shoot_x_start = x_vel * 10 + blockshead.x
        self.shoot_x_end = x_vel * self.range + blockshead.x + 1
        self.shoot_y_start = y_vel * 10 + blockshead.y
        self.shoot_y_end = y_vel * self.range + blockshead.y + 1
        self.lifetime = 3
        self.image = canvas.create_rectangle(self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end,fill="Red") # create the bullet

        self.attacked = False
        playsound('audio/uzi.wav', False)

    def contact(self, game_config, game_state):
        killed_zombies, killed_devils = [], []

        max_x, min_x = max(self.shoot_x_start, self.shoot_x_end), min(self.shoot_x_start, self.shoot_x_end)
        max_y, min_y = max(self.shoot_y_start, self.shoot_y_end), min(self.shoot_y_start, self.shoot_y_end)
        
        # Calculate damage inflicted on regular zombies
        for zombie_ix, Zombie in game_state.Zombie_Dict.items():
            cond_x = min_x - self.radius <= Zombie.x <= max_x + self.radius
            cond_y = min_y - self.radius <= Zombie.y <= max_y + self.radius
            if cond_x and cond_y:
                Zombie.injure(self.damage)
                killed_zombies.append(zombie_ix)

        # Calculate damage inflicted on devils
        for devil_ix, Zombie in game_state.Devil_Dict.items():
            cond_x = min_x - self.radius <= Zombie.x <= max_x + self.radius
            cond_y = min_y - self.radius <= Zombie.y <= max_y + self.radius

            if cond_x and cond_y:
                Zombie.injure(self.damage) # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                killed_devils.append(devil_ix)

        return killed_zombies, killed_devils

    def update(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        canvas = game_config.canvas
        if self.lifetime < 0:
            canvas.delete(self.image)
            canvas.update()
            game_state.shots.remove(self)
            return [], []

        self.lifetime -= 1

        # Update image width
        self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2
        canvas.coords(self.image, self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end)
        canvas.update()

        if not self.attacked:
            self.attacked = True
            game_state.blockshead.ammo = max(0, game_state.blockshead.ammo - 1)
            return self.contact(game_config, game_state)

        return [], []



class Fireball:
    def __init__(self, window, game_config, game_state):
        canvas = game_config.canvas
        blockshead = game_state.blockshead

        self.x = blockshead.x
        self.y = blockshead.y

        self.x_vel, self.y_vel = blockshead.direction.value
        self.x_vel, self.y_vel = self.x_vel * 5, self.y_vel * 5

        self.image = PhotoImage(file = "images/game_elements/fireball_small.png")
        self.attack = canvas.create_image(self.x,self.y,image = self.image)
        self.window = window

        game_state.blockshead.ammo = max(0, game_state.blockshead.ammo - 1)

        self.damage = 35

        playsound('audio/fireball.wav', False)

    def on_canvas(self):
        # TODO: fix coordinates based on game_config or window
        x_coord = self.x > 0 and self.x < self.window.width
        y_coord = self.y > 0 and self.y < self.window.height

        is_on_canvas = x_coord and y_coord
        return is_on_canvas
    
    def delete(self, game_config, game_state):
        print("Delete fireball...")
        game_config.canvas.delete(self.attack)
        game_config.canvas.update()
        if self in game_state.shots:
            game_state.shots.remove(self)

    def update(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        canvas = game_config.canvas
        killed_zombies, killed_devils = [], []
        if not self.on_canvas():
            self.delete(game_config, game_state)
            return killed_zombies, killed_devils

        # Update image width
        self.x += self.x_vel
        self.y += self.y_vel
        canvas.coords(self.attack, self.x, self.y)
        canvas.update()

        # Calculate damage inflicted on regular zombies
        for zombie_ix, Zombie in game_state.Zombie_Dict.items():
            if abs(Zombie.x - self.x) < 10 and abs(Zombie.y - self.y) < 10:
                Zombie.injure(self.damage)
                self.delete(game_config, game_state)
                killed_zombies.append(zombie_ix)
                return killed_zombies, killed_devils

        # Calculate damage inflicted on devils
        for devil_ix, Zombie in game_state.Devil_Dict.items():
            if abs(Zombie.x - self.x) < 10 and abs(Zombie.y - self.y) < 10:
                Zombie.injure(self.damage)
                self.delete(game_config, game_state)
                killed_devils.append(devil_ix)
                return killed_zombies, killed_devils

        return killed_zombies, killed_devils


class Healthbox(object):
    """Static object for drawing blood on the ground"""
    def __init__(self, window, game_config):
        print("Healthbox...")
        self.x = random.randrange(window.x_start, window.x_end) # create Zombies in the left half of the arena
        self.y = random.randrange(window.y_start, window.y_end)
        print(self.x, self.y)
        self.image = PhotoImage(file = "images/game_elements/healthbox.png")
        self.image_ref = game_config.canvas.create_image(self.x, self.y, image=self.image)
        self.radius = 25
        self.health = 25
        
    def update(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        canvas = game_config.canvas

        if abs(game_state.blockshead.x - self.x) < self.radius and abs(game_state.blockshead.y - self.y) < self.radius:
            game_state.blockshead.health = min(100, game_state.blockshead.health + self.health)
            game_state.healthboxes.pop(game_state.healthboxes.index(self))
            game_config.canvas.delete(self.image_ref)

