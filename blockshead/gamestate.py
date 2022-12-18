from dataclasses import dataclass

@dataclass
class GameConfig:
    canvas: bool
    background_color = "#EBDCC7"
    font = ('Helvetica','30','bold')
    weapons = {"pistol": 1, "uzi": 1, "shotgun": 5}
    ammo = {"uzi": 50, "shotgun": 15}
    multiplier_step = 0.0002
    max_health = 200
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
    multiplier = 1
    available_weapons = ["pistol"]
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