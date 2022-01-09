import numpy as np
import tkinter as tk
from tkinter import *
import random
import time
import math

class Pistol:
    def __init__(self, game_config, game_state):
        canvas = game_config.canvas
        blockshead = game_state.blockshead
        self.range = 100
        self.shoot_x_start = int(np.sign(blockshead.x_vel) * 20) + blockshead.x
        self.shoot_x_end = int(np.sign(blockshead.x_vel) * self.range) + blockshead.x + 1
        self.shoot_y_start = int(np.sign(blockshead.y_vel) * 20) + blockshead.y
        self.shoot_y_end = int(np.sign(blockshead.y_vel) * self.range) + blockshead.y + 1
        self.lifetime = 3
        self.direction = blockshead.direction
        self.image = canvas.create_rectangle(self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end,fill="Red") # create the bullet

    def update(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        canvas = game_config.canvas
        killed_zombies, killed_devils = [], []
        if self.lifetime < 0:
            canvas.delete(self.image)
            canvas.update()
            game_state.shots.remove(self)
            return killed_zombies, killed_devils

        self.lifetime -= 1

        # Update image width
        self.shoot_x_start = (self.shoot_x_start + self.shoot_x_end) // 2
        self.shoot_y_start = (self.shoot_y_start + self.shoot_y_end) // 2
        canvas.coords(self.image, self.shoot_x_start,self.shoot_y_start,self.shoot_x_end,self.shoot_y_end)
        canvas.update()

        # Calculate damage inflicted on regular zombies
        for zombie_ix, Zombie in game_state.Zombie_Dict.items():
            if self.direction == 1:
                if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                    killed_zombies.append(zombie_ix)
            elif self.direction == 2:
                if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                    killed_zombies.append(zombie_ix)
            elif self.direction == 3:
                if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                    killed_zombies.append(zombie_ix)
            elif self.direction == 4:
                if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                    killed_zombies.append(zombie_ix)

        # Calculate damage inflicted on devils
        for devil_ix, Zombie in game_state.Devil_Dict.items():
            if self.direction == 1:
                if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                    Zombie.health -= 26 # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                    killed_devils.append(devil_ix)
            elif self.direction == 2:
                if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                    Zombie.health -= 26
                    killed_devils.append(devil_ix)
            elif self.direction == 3:
                if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                    Zombie.health -= 26
                    killed_devils.append(devil_ix)
            elif self.direction == 4:
                if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                    Zombie.health -= 26
                    killed_devils.append(devil_ix)

        return killed_zombies, killed_devils


class Fireball:
    def __init__(self, game_config, game_state):
        canvas = game_config.canvas
        blockshead = game_state.blockshead

        self.x = blockshead.x
        self.y = blockshead.y

        self.x_vel = int(np.sign(blockshead.x_vel)) * 5
        self.y_vel = int(np.sign(blockshead.y_vel)) * 5

        self.direction = blockshead.direction
        self.image = PhotoImage(file = "images/game_elements/fireball_small.png")
        self.attack = canvas.create_image(self.x,self.y,image = self.image)

    def on_canvas(self):
        x_coord = self.x > 0 and self.x < 500
        y_coord = self.y > 0 and self.y < 500

        is_on_canvas = x_coord and y_coord
        print("x,y:", self.x, self.y)
        print("is_on_canvas", is_on_canvas)
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
            if abs(Zombie.x - self.x) < 10 and abs(Zombie.x - self.x) < 10:
                self.delete(game_config, game_state)
                killed_zombies.append(zombie_ix)

        # Calculate damage inflicted on devils
        for devil_ix, Zombie in game_state.Devil_Dict.items():
            if abs(Zombie.x - self.x) < 10 and abs(Zombie.x - self.x) < 10:
                Zombie.health -= 26 # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                self.delete(game_config, game_state)
                killed_devils.append(devil_ix)

        return killed_zombies, killed_devils