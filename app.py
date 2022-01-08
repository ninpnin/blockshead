import tkinter as tk
from tkinter import *
import random
import time
import math
from math import ceil
from blockshead.gamestate import *
import numpy as np

def initialize_game():
    window = WindowProperties(height=750, width=1000, x_buffer=40, y_buffer=40)
    window.x_start = 2 * window.x_buffer - 20
    window.y_start = 3 * window.y_buffer - 35
    window.x_end = window.width - window.x_buffer - 20
    window.y_end = window.height - window.y_buffer - 20

    canvas = tk.Canvas(highlightthickness=0, height=window.height, width=window.width)
    canvas.master.title("Blockshead")
    canvas.pack()
    background = canvas.create_rectangle(0, 0, window.width, window.height, fill="#EBDCC7", belowThis=None)
    pic = PhotoImage(width=window.width, height=window.height)
    canvas.create_image(0,0,image=pic,anchor=NW)
    pausescreen = canvas.create_rectangle(0, 0, window.width, window.height, fill="#EBDCC7", aboveThis=None)
    print("Pausescreen", pausescreen)

    init_state = InitState()
    game_config = GameConfig(canvas=canvas)
    game_config.background = background
    game_state = GameState()
    game_state.blockshead = Blockshead(window, game_config)
    game_state.stats = Stats(window, canvas)

    canvas.create_rectangle(0,0,(window.x_buffer),(window.y_buffer+window.height), fill="Black") # create all of the buffer images
    canvas.create_rectangle((window.x_buffer+window.width),0,(window.width-(window.x_buffer)),((2*window.y_buffer)+window.height), fill="Black")
    canvas.create_rectangle(0,0,(window.width-window.x_buffer),window.y_buffer, fill="Black")
    canvas.create_rectangle(0,(window.height-window.y_buffer),window.width,window.height, fill="Black")

    return game_config, init_state, game_state, window

def pause(toggle, canvas, screen):
    toggle = not toggle
    if pause_game:
        canvas.tag_raise(screen)
        canvas.itemconfigure(screen, state='normal')
    else:
        canvas.itemconfigure(screen, state='hidden')
    return toggle


class Blood(object):
    """What happens when you kill something. It create a blood spot on the coordinates of the killed Zombie(s) / Devil(s)
    They are deleted at the beginning of each new level"""
    def __init__(self,x,y, game_config):
        self.image = PhotoImage(file = "images/game_elements/blood.png")
        self.blood_spot = game_config.canvas.create_image(x,y,image = self.image)
        game_config.canvas.tag_lower(self.blood_spot)
        game_config.canvas.tag_lower(game_config.background)

class Zombie_Attack(object):
    """The yellow circle that the zombies uses to attack Blockshead. It has a life span of 125 instances in the while loop before it disappears.
    Unless of course it strikes blockshead and lowers blockshead's health by a lot"""
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

    def move(self, canvas, target):
        self.x += self.x_vel
        self.y += self.y_vel
        canvas.coords(self.attack,self.x,self.y)
        self.life_span -=1
        if abs(self.x - target.x) < 30 and abs(self.y - target.y) < 30: #Strike Blockshead if within 30 pixels
            target.health -= 10
            self.life_span = 0

class Stats(object):
    """Creates the score label/info. This updates once per loop based on all of Blockshead's attributes ex. health and score"""
    def __init__(self, window, canvas):
        self.board = canvas.create_text(200,65)
        canvas.create_rectangle(window.x_buffer,window.y_buffer,window.width - window.x_buffer,window.y_buffer+20,fill="Red")

    def update(self, game_config, game_state):
        health_string = str(game_state.blockshead.health)
        score_string = str(ceil(game_state.blockshead.score))
        level_string = str(game_state.blockshead.level)
        gun_string = str(game_state.blockshead.gun)
        ammo_string = str(game_state.blockshead.ammo)
        score_board = "Health: " + health_string + "  " + "Score: " + score_string + "  " + "Level: " + level_string + "  " + "Gun: " + gun_string + "  " + "Ammo: " + ammo_string
        game_config.canvas.delete(self.board)
        self.board = game_config.canvas.create_text(230,52,text=score_board)

class Blockshead(object):
    """The Blockshead charecter. Shoot, move, lay mines etc. are all contianed within the Blockshead class. Eventually all of the gun details need to be moved to thier own class so that Pistol = Gun(range,damage) and Mine = Gun(radius, damage)
    eventually even Shotgun = Gun(range,damange,arc_width) and so on"""
    def __init__(self, window, game_config):
        self.image_up = PhotoImage(file = "images/blockshead/bhup.png") # The image changes if Blockshead is facing up down left right
        self.image_down = PhotoImage(file = "images/blockshead/bhdown.png")
        self.image_left = PhotoImage(file = "images/blockshead/bhleft.png")
        self.image_right = PhotoImage(file = "images/blockshead/bhright.png")
        self.x = random.randrange(((window.x_start/2)+15),window.x_end) # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.y = random.randrange(window.y_start,window.y_end)
        self.image = game_config.canvas.create_image(self.x,self.y,image = self.image_up)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = 1
        self.health = 100 # +5 health is added at the beginning of every level
        self.gun = "Pistol"
        self.level = 1
        self.score = 0
        self.ammo = "Infinite"
        self.pause = False
        self.bonus_score = 0
        self.pistol_range = 150 # the range of the pistol in pixels
        self.mine_count = 0 # how many mines are left
        self.bullet_images = []

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
        canvas.coords(self.image,(self.x),(self.y))

    def update_sprite(self, game_config):
        """Change Blockshead's image based on the direction he is moving"""
        if self.direction == 1:
            game_config.canvas.itemconfigure(self.image, image = self.image_up)
        elif self.direction == 2:
            game_config.canvas.itemconfigure(self.image, image = self.image_down)
        elif self.direction == 3:
            game_config.canvas.itemconfigure(self.image, image = self.image_left)
        elif self.direction == 4:
            game_config.canvas.itemconfigure(self.image, image = self.image_right)

    def fire_gun(self, game_config, game_state):
        """Fires whichever weapon that blockshead is using at the moment"""
        self.bonus_score = 0
        Dead_Zombie_List = []
        which_zombie = 0
        kill_list = [] # the librarys that hold which Zombie needs to be deleted from Zombie_Dict
        kill_devil = []

        if self.gun == "Pistol":
            self.shoot_x_start = int(np.sign(self.x_vel) * 20) + self.x
            self.shoot_x_end = int(np.sign(self.x_vel) * 200) + self.x + 1
            self.shoot_y_start = int(np.sign(self.y_vel) * 20) + self.y
            self.shoot_y_end = int(np.sign(self.y_vel) * 200) + self.y + 1
            bullet_image = canvas.create_rectangle(self.shoot_x_start,self.shoot_y_start,self.shoot_x_end+1,self.shoot_y_end+1,fill="Black") # create the bullet
            self.bullet_images.append((bullet_image, 5))
            canvas.update()

            # Calculate damage inflicted on regular zombies
            for Each_Zombie, Zombie in game_state.Zombie_Dict.items():
                if self.direction == 1:
                    if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                        kill_list.append(Each_Zombie)
                elif self.direction == 2:
                    if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                        kill_list.append(Each_Zombie)
                elif self.direction == 3:
                    if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                        kill_list.append(Each_Zombie)
                elif self.direction == 4:
                    if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                        kill_list.append(Each_Zombie)

            # Calculate damage inflicted on devils
            for each_devil, Zombie in game_state.Devil_Dict.items():
                if self.direction == 1:
                    if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                        Zombie.health -= 26 # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                        kill_devil.append(each_devil)
                elif self.direction == 2:
                    if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                        Zombie.health -= 26
                        kill_devil.append(each_devil)
                elif self.direction == 3:
                    if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                        Zombie.health -= 26
                        kill_devil.append(each_devil)
                elif self.direction == 4:
                    if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                        Zombie.health -= 26
                        kill_devil.append(each_devil)

            for zombie_ix in kill_list: # Destroy the Zombie to be killed from the Zombie_Dict and canvas
                zombie = game_state.Zombie_Dict[zombie_ix]
                mark = Blood(zombie.x, zombie.y,game_config)
                game_state.blood_dict[game_state.blood_marks] = mark
                game_state.blood_marks +=1
                canvas.delete(zombie)
                del game_state.Zombie_Dict[zombie_ix]
                game_state.blockshead.score+=1
                self.bonus_score +=1

            for devil_ix in kill_devil:
                devil = game_state.Devil_Dict[devil_ix]
                mark = Blood(devil.x, devil.y,game_config)
                game_state.blood_dict[game_state.blood_marks] = mark
                game_state.blood_marks +=1
                if game_state.Devil_Dict[devil_ix].health <= 0:
                    game_config.canvas.delete(game_state.Devil_Dict[devil_ix])
                    del game_state.Devil_Dict[devil_ix]
                    game_state.blockshead.score+=1
                    self.bonus_score +=1

            self.score += (self.bonus_score / 3)

        canvas.update()

    def update_shots(self, game_config):
        for ix, bullet_image_tuple in enumerate(self.bullet_images):
            bullet_image, lifetime = bullet_image_tuple
            if lifetime < 0:
                game_config.canvas.delete(bullet_image)
                self.bullet_images.pop(ix)
            else:
                self.bullet_images[ix] = bullet_image, lifetime - 1

    def key(self, key, game_config):
        """Look at the input from the keyboard and adjust Blockshead accordingly. Movement = WASD Fire = Space Pistol = I Mines = U Pause = P Unpause = O"""
        global press,pause_game,pausescreen
        B_move_length = game_config.B_move_length
        if key == 'w':
            self.x_vel = 0
            self.y_vel = -B_move_length
            self.direction = 1
        elif key == 's':
            self.x_vel = 0
            self.y_vel = B_move_length
            self.direction = 2
        elif key == 'a':
            self.x_vel = -B_move_length
            self.y_vel = 0
            self.direction = 3
        elif key == 'd':
            self.x_vel = B_move_length
            self.y_vel = 0
            self.direction = 4
        elif key == 'space':
            self.fire_gun(game_config, game_state)
        elif key == 'p':
            pause_game = pause(game_state.pause_game, canvas, pausescreen)
        elif key == 'i':
            self.gun = "Pistol"
            self.ammo = 'Infinte'
        elif key == 'u':
            self.gun = 'Mines'
            self.ammo = self.mine_count

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
    def __init__(self):
        self.directions = ["up", "down", "right", "left", "rightdown", "rightup", "leftup", "leftdown"]
        self.images = {}
        for direction in self.directions:
            self.images[direction] = PhotoImage(file = "images/zombies/z{}.png".format(direction)) # the 8 Devil images

        self.x = random.randrange(window.x_start,(window.x_end-(window.x_end / 2))) # create Zombies in the left half of the arena
        self.y = random.randrange(window.y_start,window.y_end)
        self.direction = 1
        self.zombie = canvas.create_image(self.x,self.y, image = self.images["up"])
        self.alive = True
        self.distance_to_b = 0
        self.attacked = False

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
            game_config.canvas.coords(self.zombie,(self.x),(self.y)) # move the Zombie accordingly based on if it should move or another Zombie is in its path

    # TODO: rename to draw
    def update_sprite(self):
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

        canvas.itemconfigure(self.zombie, image = self.images.get(direction, self.images["up"]))

    def contact(self, target):
        """This is how the Zombies do damage to Blockshead. If they com in contact with Blockshead it deducts health from blockshead"""
        if abs(target.x - self.x) < 10 and abs(target.y - self.y) < 10 and self.attacked == False:
            target.health -= 1
            self.attacked = True

class Devil(object):
    """The Devil Class. They move faster than Zombies have more health and can attack Blockshead by colliding with him or by shooting him"""
    def __init__(self):
        self.x = random.randrange(window.x_start,(window.x_end-(window.x_end / 2)))
        self.y = random.randrange(window.y_start,window.y_end)
        self.direction = 1
        self.alive = True
        self.distance_to_b = 0
        self.attacked = False
        self.attack_fire = 0
        self.health = 100
        self.images = {}
        for direction in ["up", "down", "right", "left", "rightdown", "rightup", "leftup", "leftdown"]:
            self.images[direction] = PhotoImage(file = "images/devils/d{}.png".format(direction)) # the 8 Devil images

        self.devil = canvas.create_image(self.x,self.y, image = self.images["up"])

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
            canvas.coords(self.devil,(self.x),(self.y))

    def update_sprite(self):
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

        canvas.itemconfigure(self.devil, image = self.images[direction])

    def contact(self, target):
        """If a Devil comes in contact with blockshead it deducts more health than a Zombie would"""
        if abs(target.x - self.x) < 10 and abs(target.y - self.y) < 10 and self.attacked == False:
            target.health -= 2
            self.attacked = True

    def attack(self, target, game_config, game_state):
        """If the Devil is within +/- 200 pixels in the X and Y directions then it shoots a fireball at blockshead 1 time and then waits 45 loops to shoot agian"""
        if abs(target.x - self.x) < 200 and abs(target.y - self.y) < 200 and self.attack_fire > 45:
            d_attack = Zombie_Attack(self.x,self.y,self.x_vel,self.y_vel, game_config.canvas)
            total_devil_attacks = len(game_state.Devil_Attack_Dict)
            game_state.Devil_Attack_Dict[total_devil_attacks] = d_attack
            self.attack_fire = 0
        else:
            self.attack_fire += 1

def new_level(game_config, game_state):
    """For every new level all of the Devils and Zombies have been killed so new ones need to be created. Each time 70% more Zombies are added"""
    build_zombie = 0
    build_devil = 0
    for i in range(game_config.Number_of_Zombies):
        z = Zombie()
        game_state.Zombie_Dict[build_zombie] = z
        build_zombie += 1

    for i in range(int(game_config.Number_of_Zombies / 5)):
        D = Devil()
        game_state.Devil_Dict[build_devil] = D
        build_devil +=1

    game_state.blockshead.health += 5 
    game_state.blockshead.mine_count += int(game_config.Number_of_Zombies / 5)
    game_state.blockshead.level += 1
    
    print("New level:", game_state.blockshead.level)
    return game_config, game_state

def end_game(score, level):
    score = str(ceil(score))
    level = str((level - 1))
    text = 'Game Over! Final Score: ' + score + ' Final Level: ' + level
    print(text)

# TODO: incorporate the contents of blockshead.key and blockshead.keyup into the following functions
def key_press(event, game_config, init_state, game_state, window):
    press = event.keysym
    if press == "g":
        startgame(game_config, init_state, game_state, window)
    else:
        game_state.blockshead.key(press, game_config)

def key_release(event, game_state):
    release = event.keysym
    game_state.blockshead.keyup(release)

def main_loop(game_config, init_state, game_state, window, levelup=False):
    if not init_state.game_started:
        init_state.game_started = True

    if game_state.blockshead.health <= 0:
        end_game(game_state.blockshead.score, game_state.blockshead.level - 1)
    else:
        if not game_state.pause_game:
            if levelup:
                new_level(game_config, game_state)
            for zombie in game_state.Zombie_Dict.values():
                zombie.move(game_state.blockshead, window, game_config, game_state)
                zombie.update_sprite()
                zombie.contact(game_state.blockshead)
            for devil in game_state.Devil_Dict.values():
                devil.move(game_state.blockshead, window, game_config, game_state)
                devil.attack(game_state.blockshead, game_config, game_state)
                devil.update_sprite()
                devil.contact(game_state.blockshead)

            for attack_name, attack in list(game_state.Devil_Attack_Dict.items()):
                attack.move(canvas, game_state.blockshead)
                if attack.life_span <= 0:
                    canvas.delete(attack.attack)
                    del game_state.Devil_Attack_Dict[attack_name]

            game_state.blockshead.move(window, game_config.canvas)
            game_state.blockshead.update_shots(game_config)
            game_state.blockshead.update_sprite(game_config)
            #game_state.blockshead.update_shot_coords()
            game_state.stats.update(game_config, game_state)
        else:
            pass

        # Move to the next level if there are no enemies left
        levelup = len(game_state.Zombie_Dict) == 0 and len(game_state.Devil_Dict) == 0

        canvas.update()
        canvas.after(5, lambda: main_loop(game_config, init_state, game_state, window, levelup))

def startgame(game_config, init_state, game_state, window):
    print("startgame")
    game_config.canvas.after(30, lambda: main_loop(game_config, init_state, game_state, window))
    game_config.canvas.bind("<KeyRelease>", lambda event: key_release(event, game_state))

if __name__ == "__main__":
    game_config, init_state, game_state, window = initialize_game()
    canvas = game_config.canvas
    canvas.bind("<1>", lambda event: canvas.focus_set())
    canvas.bind("<Key>", lambda event: key_press(event, game_config, init_state, game_state, window))

    canvas.pack()
    canvas.mainloop()