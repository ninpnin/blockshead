from dataclasses import dataclass

@dataclass
class GameConfig:
    canvas: bool
    background_color = "#EBDCC7"
    font = ('Helvetica','30','bold')
    weapons = {"pistol": 1, "uzi": 1, "shotgun": 0}
    ammo = {"uzi": 100, "shotgun": 20}
    multiplier_step = 0.0002
    blockshead_speed = 2.0
    zombie_speed = 0.5
    max_health = 200
    map_width = 2000
    map_height = 1500
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
    max_ammo = {"pistol": "infinity"}
    shots = []
    mines = []
    zombies = []
    devils = []
    devil_attacks = []
    blood_marks = []
    healthboxes = []
    fakewalls = []
    messages = []
    score: int = 0
    level: int = 0
    offset_x = 0
    offset_y = 0

@dataclass
class Shots:
    direction: int
    x: int
    y: int