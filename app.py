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
    
    init_state = InitState()
    game_config = GameConfig(canvas=canvas)
    game_state = GameState()

    # Background
    background = canvas.create_rectangle(0, 0, window.width, window.height, fill=game_config.background_color, belowThis=None)
    game_config.background = background

    # Blockshead
    game_state.blockshead = Blockshead(window, game_config)
    game_state.stats = None

    # Borders
    canvas.create_rectangle(0,0,(window.x_buffer),(window.y_buffer+window.height), fill="Black") # create all of the buffer images
    canvas.create_rectangle((window.x_buffer+window.width),0,(window.width-(window.x_buffer)),((2*window.y_buffer)+window.height), fill="Black")
    canvas.create_rectangle(0,0,(window.width-window.x_buffer),window.y_buffer, fill="Black")
    canvas.create_rectangle(0,(window.height-window.y_buffer),window.width,window.height, fill="Black")

    # Start screen
    init_state.startscreen = canvas.create_rectangle(0, 0, window.width, window.height, fill=game_config.background_color, belowThis=None)
    init_state.starttext = canvas.create_text(window.width // 2, window.height // 2, text="Start game by pressing 'G'", fill="Black", font=game_config.font)

    # Pause screen
    game_config.pausescreen = canvas.create_rectangle(0, 0, window.width, window.height, fill="#EBDCC7", aboveThis=None)
    game_config.pausetext = canvas.create_text(window.width // 2, window.height // 2, text="Paused", fill="Black", font=game_config.font)
    canvas.itemconfigure(game_config.pausescreen, state='hidden')
    canvas.itemconfigure(game_config.pausetext, state='hidden')

    # Stats
    game_config.stats = canvas.create_text(200,65)
    canvas.create_rectangle(window.x_buffer,window.y_buffer,window.width - window.x_buffer,window.y_buffer+20,fill="Red")

    return game_config, init_state, game_state, window

def startgame(game_config, init_state, game_state, window):
    print("startgame")
    game_config.canvas.delete(init_state.startscreen)
    game_config.canvas.delete(init_state.starttext)
    game_config.canvas.after(30, lambda: main_loop(game_config, init_state, game_state, window))
    game_config.canvas.bind("<KeyRelease>", lambda event: key_release(event, game_state))

def pause_game(game_config, game_state):
    if not game_state.paused:
        game_config.canvas.tag_raise(game_config.pausescreen)
        game_config.canvas.itemconfigure(game_config.pausescreen, state='normal')
        game_config.canvas.tag_raise(game_config.pausetext)
        game_config.canvas.itemconfigure(game_config.pausetext, state='normal')
        game_state.paused = True
    else:
        game_config.canvas.itemconfigure(game_config.pausescreen, state='hidden')
        game_config.canvas.itemconfigure(game_config.pausetext, state='hidden')
        game_state.paused = False

def end_game(window, game_config, game_state):
    background = game_config.canvas.create_rectangle(0, 0, window.width, window.height, fill=game_config.background_color, aboveThis=None)
    end_text = 'Game Over!\nFinal Score: {}, Final Level: {}'.format(ceil(game_state.score), game_state.level -1)
    game_config.canvas.create_text(window.width // 2, window.height // 2, text=end_text, fill="Black", font=game_config.font)

def update_stats(game_config, game_state):
    # Refactor to change text content instead of creating a new object
    health_string = str(game_state.blockshead.health)
    score_string = str(ceil(game_state.score))
    level_string = str(game_state.level)
    gun_string = str(game_state.blockshead.gun)
    ammo_string = str(game_state.blockshead.ammo)
    score_board = "Health: " + health_string + "  " + "Score: " + score_string + "  " + "Level: " + level_string + "  " + "Gun: " + gun_string + "  " + "Ammo: " + ammo_string
    game_config.canvas.delete(game_config.stats)
    game_config.stats = game_config.canvas.create_text(230,52,text=score_board)

def new_level(game_config, game_state, window):
    """For every new level all of the Devils and Zombies have been killed so new ones need to be created. Each time 70% more Zombies are added"""
    build_zombie = 0
    build_devil = 0
    for i in range(game_config.Number_of_Zombies + game_state.level // 2):
        z = Zombie(window, game_config)
        game_state.Zombie_Dict[build_zombie] = z
        build_zombie += 1

    for i in range(game_config.Number_of_Zombies // 5 + game_state.level // 3):
        D = Devil(window, game_config)
        game_state.Devil_Dict[build_devil] = D
        build_devil +=1

    hb = Healthbox(window, game_config)
    game_state.healthboxes.append(hb)
    game_state.blockshead.health = min(100, 5 + game_state.blockshead.health) 
    game_state.blockshead.mine_count += int(game_config.Number_of_Zombies / 5)
    game_state.level += 1
    
    print("New level:", game_state.level)
    return game_config, game_state

# TODO: incorporate the contents of blockshead.key and blockshead.keyup into the following functions
def key_press(event, game_config, init_state, game_state, window):
    pressed_character = event.keysym
    if pressed_character == "g":
        startgame(game_config, init_state, game_state, window)
    elif pressed_character == "p":
        print("Pause game")
        pause_game(game_config, game_state)
    else:
        game_state.blockshead.key(pressed_character, window, game_config, game_state)

def key_release(event, game_state):
    released_character = event.keysym
    game_state.blockshead.keyup(released_character)

def main_loop(game_config, init_state, game_state, window, levelup=False):
    if not init_state.game_started:
        init_state.game_started = True

    if game_state.blockshead.health <= 0:
        end_game(window, game_config, game_state)
    else:
        if not game_state.paused:
            if levelup:
                new_level(game_config, game_state, window)
            for zombie in game_state.Zombie_Dict.values():
                zombie.move(game_state.blockshead, window, game_config, game_state)
                zombie.update_sprite(game_config)
                zombie.contact(game_state.blockshead)
            for devil in game_state.Devil_Dict.values():
                devil.move(game_state.blockshead, window, game_config, game_state)
                devil.attack(game_state.blockshead, game_config, game_state)
                devil.update_sprite(game_config)
                devil.contact(game_state.blockshead)

            for attack_name, attack in list(game_state.Devil_Attack_Dict.items()):
                attack.move(canvas, game_state.blockshead)
                if attack.life_span <= 0:
                    canvas.delete(attack.attack)
                    del game_state.Devil_Attack_Dict[attack_name]

            for healthbox in list(game_state.healthboxes):
                healthbox.update(game_config, game_state)

            game_state.blockshead.move(window, game_config.canvas)
            game_state.blockshead.update_shots(game_config, game_state)
            game_state.blockshead.update_sprite(game_config)
            update_stats(game_config, game_state)
        else:
            pass

        # Move to the next level if there are no enemies left
        levelup = len(game_state.Zombie_Dict) == 0 and len(game_state.Devil_Dict) == 0

        canvas.update()
        canvas.after(5, lambda: main_loop(game_config, init_state, game_state, window, levelup))

if __name__ == "__main__":
    game_config, init_state, game_state, window = initialize_game()
    canvas = game_config.canvas
    canvas.bind("<1>", lambda event: canvas.focus_set())
    canvas.bind("<Key>", lambda event: key_press(event, game_config, init_state, game_state, window))

    canvas.pack()
    canvas.mainloop()