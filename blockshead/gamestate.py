from dataclasses import dataclass

@dataclass
class WindowProperties:
    height: int
    width: int
    x_buffer: int
    y_buffer: int

@dataclass
class GameConfig:
    B_move_length = 2 # Some the game attributes that change and are used for the initial setup. Most would be better in a central Game Class
    Zombie_per_move = .5
    Devil_move = 1
    shot_duration = .01
    kill_zone = 15
    Number_of_Zombies = 5
    canvas: bool
    Zombie_Buffer = 30

@dataclass
class Screen:
    a: int

@dataclass
class InitState:
    Zombie_Dict_Made = False # have the Zombies and Blockshead been created?
    blockshead_made = False
    Run_Game = True
    New_Level = False
    game_started = False

@dataclass
class GameState:
    direction = 1
    Number_of_Zombies = 5
    total_devil_attacks = 0
    blood_marks = 0
    number_of_mines = 0

    pause_game = False

    shots = set()
    Mines_Dict = {} # holds all of the mines
    Zombie_Dict = {} # Where the Zombies are kept - elements are deleted as Blockshead shoots them
    Devil_Dict = {} # same as Zombie_Dict but for Devils
    Dead_Zombie_List = []
    Devil_Attack_Dict = {} # The spheres that the Devils can attack with
    blood_dict = {}

    score: int = 0
    level: int = 1

@dataclass
class Shots:
    direction: int
    x: int
    y: int