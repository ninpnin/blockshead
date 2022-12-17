import pygame
import random
import numpy as np
from .objects import Direction
from .objects import Pistol, Uzi, Fireball, DevilAttack, Blood

class Blockshead(object):
    """The Blockshead charecter. Shoot, move, lay mines etc. are all contianed within the Blockshead class. Eventually all of the gun details need to be moved to thier own class so that Pistol = Gun(range,damage) and Mine = Gun(radius, damage)
    eventually even Shotgun = Gun(range,damange,arc_width) and so on"""
    def __init__(self, game_config):
        self.images = {}
        self.images[Direction.UP] = pygame.image.load("images/blockshead/bhup.png") # PhotoImage(file = "images/blockshead/bhup.png") # The image changes if Blockshead is facing up down left right
        self.images[Direction.DOWN] = None #PhotoImage(file = "images/blockshead/bhdown.png")
        self.images[Direction.LEFT] = None #PhotoImage(file = "images/blockshead/bhleft.png")
        self.images[Direction.RIGHT] = None #PhotoImage(file = "images/blockshead/bhright.png")
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
    
    def get_image(self):
        return self.images[self.direction]
    """
    
    def move(self, window, canvas, game_state):
        if (self.x >= window.x_end) and self.x_vel > 0:
            self.x_vel = 0
        elif self.x <= window.x_start and self.x_vel < 0:
            self.x_vel = 0

        if (self.y >= window.y_end) and self.y_vel > 0:
            self.y_vel = 0
        elif self.y <= window.y_start and self.y_vel < 0:
            self.y_vel = 0

        next_x = self.x + self.x_vel * 2
        next_y = self.y + self.y_vel * 2
        radius = 5
        max_x, min_x = max(next_x, self.x), max(next_x, self.x)
        max_y, min_y = max(next_y, self.y), max(next_y, self.y)

        if max_x == min_x:
            max_x += radius
            min_x -= radius
        if max_y == min_y:
            max_y += radius
            min_y -= radius

        for zombie in game_state.Zombie_Dict.values():
            if min_x <= zombie.x <= max_x and min_y <= zombie.y <= max_y:
                self.x_vel, self.y_vel = 0, 0

        for devil in game_state.Devil_Dict.values():
            if min_x <= devil.x <= max_x and min_y <= devil.y <= max_y:
                self.x_vel, self.y_vel = 0, 0

        for fakewall in game_state.fakewalls:
            if min_x <= fakewall.x <= max_x and min_y <= fakewall.y <= max_y:
                self.x_vel, self.y_vel = 0, 0

        self.x += self.x_vel
        self.y += self.y_vel
        self.cooldown = max(0, self.cooldown - 1)

    def update_sprite(self, game_config):
        
        game_config.canvas.itemconfigure(self.image, image = self.images[self.direction])
        game_config.canvas.coords(self.image,(self.x),(self.y))

        # Health bar
        width = int(40 * self.health / 100)
        game_config.canvas.coords(self.healthbar,self.x -20 + width, self.y -55, self.x - 20, self.y - 60)
        game_config.canvas.coords(self.healthbar_bg,self.x + 20, self.y -55, self.x - 20, self.y - 60)
        game_config.canvas.tag_raise(self.healthbar_bg)
        game_config.canvas.tag_raise(self.healthbar)

    def fire_gun(self, window, game_config, game_state):
        self.bonus_score = 0
        if self.cooldown == 0:
            if self.gun == "Pistol":
                shot = Pistol(game_config, game_state)
                self.cooldown = 20
                game_state.shots.add(shot)
            elif self.gun == "Uzi":
                if game_state.blockshead.ammo > 0:
                    shot = Uzi(game_config, game_state)
                    self.cooldown = 10
                    game_state.shots.add(shot)
            elif self.gun == "Fireball":
                if game_state.blockshead.ammo > 0:
                    shot = Fireball(window, game_config, game_state)
                    self.cooldown = 30
                    game_state.shots.add(shot)

    def update_shots(self, game_config, game_state):
        kill_list, kill_devil = [], []
        for shot in list(game_state.shots):
            killed_zombies, killed_devils = shot.update(game_config, game_state)
            kill_list, kill_devil = kill_list + killed_zombies, kill_devil + killed_devils

        # Kill the zombies that have run out of health
        for zombie_ix in kill_list:
            zombie = game_state.Zombie_Dict[zombie_ix]
            if game_state.Zombie_Dict[zombie_ix].health <= 0:
                game_config.canvas.delete(zombie)
                del game_state.Zombie_Dict[zombie_ix]
                mark = Blood(zombie.x, zombie.y,game_config)
                game_state.blood_marks.add(mark)
                game_state.score+=1
                self.bonus_score +=1

        # Kill the devils that have run out of health
        for devil_ix in kill_devil:
            devil = game_state.Devil_Dict[devil_ix]
            if game_state.Devil_Dict[devil_ix].health <= 0:
                game_config.canvas.delete(game_state.Devil_Dict[devil_ix])
                mark = Blood(devil.x, devil.y,game_config)
                game_state.blood_marks.add(mark)
                del game_state.Devil_Dict[devil_ix]
                game_state.score+=1
                self.bonus_score +=1

            game_state.score += (self.bonus_score / 3)

        game_config.canvas.update()

    """
