import tkinter as tk
from tkinter import *
import random
import time
import math
from math import ceil
from blockshead.gamestate import *
from blockshead.characters import Blockshead, Zombie, Devil
from blockshead.objects import *
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
    
    # TODO: fix pause screen
    # pausescreen = canvas.create_rectangle(0, 0, window.width, window.height, fill="#EBDCC7", aboveThis=None)
    # print("Pausescreen", pausescreen)

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

def new_level(game_config, game_state, window):
    """For every new level all of the Devils and Zombies have been killed so new ones need to be created. Each time 70% more Zombies are added"""
    build_zombie = 0
    build_devil = 0
    for i in range(game_config.Number_of_Zombies):
        z = Zombie(window, game_config)
        game_state.Zombie_Dict[build_zombie] = z
        build_zombie += 1

    for i in range(int(game_config.Number_of_Zombies / 5)):
        D = Devil(window, game_config)
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
                new_level(game_config, game_state, window)
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
            game_state.blockshead.update_shots(game_config, game_state)
            game_state.blockshead.update_sprite(game_config)
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