from dataclasses import dataclass

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
    background_color = "#EBDCC7"
    font = ('Helvetica','30','bold')
    height: int
    width: int

@dataclass
class GameState:
    direction = 1
    number_of_zombies = 5
    total_devil_attacks = 0
    blood_marks = 0
    number_of_mines = 0

    paused = False

    shots = []
    mines = []
    zombies = []
    devils = []
    devil_attacks = []
    blood_marks = []
    healthboxes = []
    fakewalls = []
    score: int = 0
    level: int = 0

@dataclass
class Shots:
    direction: int
    x: int
    y: int