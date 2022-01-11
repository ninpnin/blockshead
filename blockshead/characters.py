import tkinter as tk
from tkinter import *
import random
import numpy as np
from .objects import Direction
from .objects import Pistol, Uzi, Fireball, DevilAttack, Blood

class Blockshead(object):
    """The Blockshead charecter. Shoot, move, lay mines etc. are all contianed within the Blockshead class. Eventually all of the gun details need to be moved to thier own class so that Pistol = Gun(range,damage) and Mine = Gun(radius, damage)
    eventually even Shotgun = Gun(range,damange,arc_width) and so on"""
    def __init__(self, window, game_config):
        self.images = {}
        self.images[Direction.UP] = PhotoImage(file = "images/blockshead/bhup.png") # The image changes if Blockshead is facing up down left right
        self.images[Direction.DOWN] = PhotoImage(file = "images/blockshead/bhdown.png")
        self.images[Direction.LEFT] = PhotoImage(file = "images/blockshead/bhleft.png")
        self.images[Direction.RIGHT] = PhotoImage(file = "images/blockshead/bhright.png")
        self.x = random.randrange(((window.x_start/2)+15),window.x_end) # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.y = random.randrange(window.y_start,window.y_end)
        self.direction = Direction.UP
        self.image = game_config.canvas.create_image(self.x,self.y,image = self.images[self.direction])
        self.healthbar_bg = game_config.canvas.create_rectangle(self.x + 20, self.y -55, self.x - 20, self.y - 60, fill="Red", belowThis=None)
        self.healthbar = game_config.canvas.create_rectangle(self.x + 20, self.y -55, self.x - 20, self.y - 60, fill="Green", belowThis=None)
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

    def move(self, window, canvas):
        if (self.x >= window.x_end) and self.x_vel > 0: # Can blockshead move in that direction or will he strike the edge of the game
            self.x_vel = 0
        elif self.x <= window.x_start and self.x_vel < 0:
            self.x_vel = 0

        if (self.y >= window.y_end) and self.y_vel > 0:
            self.y_vel = 0
        elif self.y <= window.y_start and self.y_vel < 0:
            self.y_vel = 0

        self.x += self.x_vel
        self.y += self.y_vel
        self.cooldown = max(0, self.cooldown - 1)

    def update_sprite(self, game_config):
        """Change Blockshead's image based on the direction he is moving"""
        game_config.canvas.itemconfigure(self.image, image = self.images[self.direction])
        game_config.canvas.coords(self.image,(self.x),(self.y))

        # Health bar
        width = int(40 * self.health / 100)
        game_config.canvas.coords(self.healthbar,self.x -20 + width, self.y -55, self.x - 20, self.y - 60)
        game_config.canvas.coords(self.healthbar_bg,self.x + 20, self.y -55, self.x - 20, self.y - 60)
        game_config.canvas.tag_raise(self.healthbar_bg)
        game_config.canvas.tag_raise(self.healthbar)

    def fire_gun(self, window, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        self.bonus_score = 0
        if self.cooldown == 0:
            if self.gun == "Pistol":
                shot = Pistol(game_config, game_state)
                self.cooldown = 10
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
            mark = Blood(zombie.x, zombie.y,game_config)
            game_state.blood_dict[game_state.blood_marks] = mark
            game_state.blood_marks +=1
            if game_state.Zombie_Dict[zombie_ix].health <= 0:
                game_config.canvas.delete(zombie)
                del game_state.Zombie_Dict[zombie_ix]
                game_state.score+=1
                self.bonus_score +=1

        # Kill the devils that have run out of health
        for devil_ix in kill_devil:
            devil = game_state.Devil_Dict[devil_ix]
            mark = Blood(devil.x, devil.y,game_config)
            game_state.blood_dict[game_state.blood_marks] = mark
            game_state.blood_marks +=1
            if game_state.Devil_Dict[devil_ix].health <= 0:
                game_config.canvas.delete(game_state.Devil_Dict[devil_ix])
                del game_state.Devil_Dict[devil_ix]
                game_state.score+=1
                self.bonus_score +=1

            game_state.score += (self.bonus_score / 3)

        game_config.canvas.update()

    def key(self, key, window, game_config, game_state):
        B_move_length = game_config.B_move_length
        if key == 'w':
            self.x_vel = 0
            self.y_vel = -B_move_length
            self.direction = Direction.UP
        elif key == 's':
            self.x_vel = 0
            self.y_vel = B_move_length
            self.direction = Direction.DOWN
        elif key == 'a':
            self.x_vel = -B_move_length
            self.y_vel = 0
            self.direction = Direction.LEFT
        elif key == 'd':
            self.x_vel = B_move_length
            self.y_vel = 0
            self.direction = Direction.RIGHT
        elif key == 'space':
            self.fire_gun(window, game_config, game_state)
        elif key == '1':
            self.gun = "Pistol"
            self.ammo = 'Infinite'
        elif key == '2':
            self.gun = "Uzi"
            self.ammo = 50
        elif key == '8':
            self.gun = 'Fireball'
            self.ammo = 10

    def keyup(self, key):
        if key in ['w', 's']:
            self.y_vel = 0
        elif key in ['a', 'd']:
            self.x_vel = 0

    def shoot_coords(self,x_start,y_start,x_end,y_end):
        """Help to adjust the coordinates based on where to shoot from each direction"""
        self.shoot_x_start = x_start
        self.shoot_y_start = y_start
        self.shoot_x_end = x_end
        self.shoot_y_end = y_end

class Zombie(object):
    """ZOMBIES. Nothing like a bunch of Zombies that chase you around. Blockshead is faster then Zombies, but Zombies can move diagonally"""
    def __init__(self, window, game_config):
        self.direction = Direction.UP
        self.images = {}
        for direction in Direction:
            self.images[direction] = PhotoImage(file = "images/zombies/z{}.png".format(direction.name.lower())) # the 8 Devil images

        self.x = random.randrange(window.x_start,(window.x_end-(window.x_end / 2))) # create Zombies in the left half of the arena
        self.y = random.randrange(window.y_start,window.y_end)
        
        self.zombie = game_config.canvas.create_image(self.x,self.y, image = self.images[self.direction])
        self.health = 50
        self.cooldown = 0

    def move(self, target, window, game_config, game_state):
        """
        This function like Blockshead1.move tests to see whether the Zombie will hit the edge of the game,
        but also tests to see whether the Zombie will collide with another Zombie in front of it. This helps
        avoid having all of the Zombies stack up on top of each other and froming one really dense Zombie.
        That is what the really long line of code below is testing
        """
        which_zombie = 0
        collision = False
        self.x_vel = 0
        self.y_vel = 0
        blockshead = game_state.blockshead
        for which_zombie in game_state.Zombie_Dict:
            test_self = game_state.Zombie_Dict[which_zombie]
            condition1x = abs(self.x - blockshead.x) - abs(blockshead.x - test_self.x) > 0
            condition2x = abs(self.x - blockshead.x) - abs(blockshead.x - test_self.x) < game_config.Zombie_Buffer
            condition1y =  abs(self.y - blockshead.y) - abs(blockshead.y - test_self.y) > 0
            condition2y = abs(self.y - blockshead.y) - abs(blockshead.y - test_self.y) < game_config.Zombie_Buffer
            if condition1x and condition2x and condition1y and condition2y:
                collision = True

        if not collision:
            self.x_vel = - game_config.Zombie_per_move * np.sign(self.x - target.x)
            self.y_vel = - game_config.Zombie_per_move * np.sign(self.y - target.y)

            if self.x >= window.width - 25: # x coords
                self.x_vel = -game_config.Zombie_per_move
            if self.x <= 0 + 5:
                self.x_vel = game_config.Zombie_per_move
            if self.y >= window.height - 25:# y coords
                self.y_vel = -game_config.Zombie_per_move
            if self.y <= 0 + 5:
                self.y_vel = game_config.Zombie_per_move
            self.y += self.y_vel
            self.x += self.x_vel
             # move the Zombie accordingly based on if it should move or another Zombie is in its path
        if self.cooldown > 0:
            self.cooldown -= 1

    # TODO: rename to draw
    def update_sprite(self, game_config):
        """Update the Zombie image based on which of the 8 directions that it is traveling in"""
        direction = ""
        if self.x_vel < 0:
            direction += "left"
        elif self.x_vel > 0:
            direction += "right"
        if self.y_vel < 0:
            direction += "up"
        elif self.y_vel > 0:
            direction += "down"

        # Load new sprite if direction has changed
        if direction != "" and direction != self.direction.name.lower():
            self.direction = Direction[direction.upper()]
            game_config.canvas.itemconfigure(self.zombie, image = self.images.get(direction, self.images[self.direction]))

        game_config.canvas.coords(self.zombie,(self.x),(self.y))

    def contact(self, target):
        """This is how the Zombies do damage to Blockshead. If they com in contact with Blockshead it deducts health from blockshead"""
        if abs(target.x - self.x) < 10 and abs(target.y - self.y) < 10 and self.cooldown == 0:
            target.health -= 1
            self.cooldown = 5

class Devil(object):
    """The Devil Class. They move faster than Zombies have more health and can attack Blockshead by colliding with him or by shooting him"""
    def __init__(self, window, game_config):
        self.x = random.randrange(window.x_start,(window.x_end-(window.x_end / 2)))
        self.y = random.randrange(window.y_start,window.y_end)
        self.direction = Direction.UP
        self.cooldown = 0
        self.attack_fire = 0
        self.health = 100
        self.images = {}
        for direction in Direction:
            self.images[direction] = PhotoImage(file = "images/devils/d{}.png".format(direction.name.lower()))

        self.devil = game_config.canvas.create_image(self.x,self.y, image = self.images[self.direction])

    def move(self, target, window, game_config, game_state):
        """The Devil's movement is the same as the Zombies except that Devils move faster"""
        which_zombie = 0
        collision = False
        self.x_vel = 0
        self.y_vel = 0
        for the_devil in game_state.Devil_Dict:
            test_self = game_state.Devil_Dict[the_devil]
            if (abs(self.x - target.x) - abs(target.x - test_self.x) > 0
            and abs(self.x - target.x) - abs(target.x - test_self.x) < game_state.Zombie_Buffer
            and abs(self.y - target.y) - abs(target.y - test_self.y) > 0
            and abs(self.y - target.y) - abs(target.y - test_self.y) < game_state.Zombie_Buffer):
                collision = True

        if not collision:
            self.x_vel = - game_config.Devil_move * np.sign(self.x - target.x)
            self.y_vel = - game_config.Devil_move * np.sign(self.y - target.y)

            if self.x >= window.width - 25: # x coords
                self.x_vel = - game_config.Devil_move
            if self.x <= 0 + 5:
                self.x_vel = game_config.Devil_move
            if self.y < target.y:
                self.y_vel = game_config.Devil_move
            if self.y > target.y:
                self.y_vel = -game_config.Devil_move
            elif self.y == target.y:
                self.y_vel = 0
            if self.y >= window.height - 25:# y coords
                self.y_vel = -game_config.Devil_move
            if self.y <= 0 + 5:
                self.y_vel = game_config.Devil_move
            self.y += self.y_vel
            self.x += self.x_vel
        if self.cooldown > 0:
            self.cooldown -= 1

    def update_sprite(self, game_config):
        """Update the Zombie image based on which of the 8 directions that it is traveling in"""
        direction = ""
        if self.x_vel < 0:
            direction += "left"
        elif self.x_vel > 0:
            direction += "right"
        if self.y_vel < 0:
            direction += "up"
        elif self.y_vel > 0:
            direction += "down"

        if direction != "" and direction != self.direction.name.lower():
            self.direction = Direction[direction.upper()]
            game_config.canvas.itemconfigure(self.devil, image = self.images[self.direction])
        
        game_config.canvas.coords(self.devil,(self.x),(self.y))

    def contact(self, target):
        """If a Devil comes in contact with blockshead it deducts more health than a Zombie would"""
        if abs(target.x - self.x) < 10 and abs(target.y - self.y) < 10 and self.cooldown == 0:
            target.health -= 2
            self.cooldown = 5

    def attack(self, target, game_config, game_state):
        """If the Devil is within +/- 200 pixels in the X and Y directions then it shoots a fireball at blockshead 1 time and then waits 45 loops to shoot agian"""
        if abs(target.x - self.x) < 200 and abs(target.y - self.y) < 200 and self.attack_fire > 45:
            d_attack = DevilAttack(self.x,self.y,self.x_vel,self.y_vel, game_config.canvas)
            total_devil_attacks = len(game_state.Devil_Attack_Dict)
            game_state.Devil_Attack_Dict[total_devil_attacks] = d_attack
            self.attack_fire = 0
        else:
            self.attack_fire += 1

