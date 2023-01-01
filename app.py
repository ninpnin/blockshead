from tkinter import W
from blockshead.gamestate import *
from blockshead.characters import Blockshead, Zombie, Devil
from blockshead.objects import *
import pygame
from pygame import mixer
import math
from numpy.random import choice as np_choice

def initialize_game():
    pygame.init()
    pygame.display.set_caption('Blockshead')
    game_config = GameConfig(canvas=None, width=1000, height=750)
    screen = pygame.display.set_mode([game_config.width, game_config.height])
    game_state = GameState()
    game_state.blockshead = Blockshead(game_config)
    return game_config, game_state, screen

def draw_pause_screen(window, game_config):
    window.fill(game_config.background_color)
    font = pygame.font.SysFont(None, 36)
    img = font.render("Paused. Press 'P' to continue", True, (100,100,100))
    window.blit(img, (20, 20))
    
def draw_stats(window, game_state, game_config):
    # Left corner title
    font = pygame.font.SysFont(None, 36)
    img = font.render(f'Level: {game_state.level}, Points: {game_state.score}', True, (100,100,100))
    window.blit(img, (20, 20))
    img = font.render(f'Weapon: {game_state.blockshead.weapon}', True, (100,100,100))
    window.blit(img, (20, 60))
    img = font.render(f'Ammo: {game_state.blockshead.ammo()}', True, (100,100,100))
    window.blit(img, (20, 100))

    # Right corner title
    font = pygame.font.SysFont(None, 36)
    img = font.render(f'Multiplier: {game_state.multiplier:.2f}', True, (100,100,100))
    window.blit(img, (game_config.width - 200, 20))

    # Health bar
    health = game_state.blockshead.health
    healthbar_width = int(100 * health/game_config.max_health)
    start_x = - 40 + game_state.blockshead.x - game_state.offset_x
    start_y = game_state.blockshead.y - 70 - game_state.offset_y
    pygame.draw.rect(window, (255,0,0), (start_x, start_y, 100, 10))
    pygame.draw.rect(window, (0,128,0), (start_x, start_y, healthbar_width, 10))

def draw_messages(window, game_state, game_config):
    # Left corner title
    game_state.messages = [(m, t -1) for m,t in game_state.messages if t >= 1]
    x, y = game_config.width // 2 - 200, 20
    for m, _ in game_state.messages:
        font = pygame.font.SysFont(None, 36)
        img = font.render(m, True, (100,100,100))
        window.blit(img, (x, y))
        y += 40

def add_zombies(game_config, game_state, window):
    x = random.randrange(40, game_config.width // 20)
    if random.choice([True, False]):
        x = game_config.width - x
    y = random.randrange(40, game_config.height -40)

    if game_state.level_zombies >= 1:
        zombie = Zombie(window, game_config, init_coords=(x,y))
        if not zombie._check_collisions(game_state, game_config):
            game_state.zombies.append(zombie)
            game_state.level_zombies -= 1
            print("Add zombie...")
            
    #return game_config, game_state
        
def new_level(game_config, game_state, window):
    game_state.number_of_zombies += 2
    game_state.level_zombies = game_state.number_of_zombies
    game_state.zombies = []
    
    while len(game_state.devils) < 1:
        devil = Devil(window, game_config)
        if not devil._check_collisions(game_state, game_config):
            game_state.devils.append(devil)

    healthbox_x = random.randrange(0, game_config.width)
    healthbox_y = random.randrange(0, game_config.height)
    healthbox = Healthbox(game_state, healthbox_x, healthbox_y)
    game_state.healthboxes.append(healthbox)
    
    for blood_mark in game_state.blood_marks:
        blood_mark.levelup()
        
    game_state.level += 1
    game_state.messages.append((f"Level {game_state.level}", 180))
    
    newlevel_audio = pygame.mixer.Sound('audio/new-level.mp3')
    mixer.Channel(1).play(newlevel_audio)
    #mixer.music.play()

    return game_config, game_state, window

def handle_keys(event, window, game_config, game_state):
    if event.type == pygame.KEYDOWN:
        if not game_state.paused:
            # Game controls
            if event.key == pygame.K_LEFT:
                game_state.blockshead.x_vel = -1
                game_state.blockshead.direction = Direction.LEFT
            if event.key == pygame.K_RIGHT:
                game_state.blockshead.x_vel = 1
                game_state.blockshead.direction = Direction.RIGHT
            if event.key == pygame.K_UP:
                game_state.blockshead.y_vel = -1
                game_state.blockshead.direction = Direction.UP
            if event.key == pygame.K_DOWN:
                game_state.blockshead.y_vel = 1
                game_state.blockshead.direction = Direction.DOWN
                
            if event.key == pygame.K_SPACE:
                shot = game_state.blockshead.fire_gun(window, game_config, game_state)
                if shot is not None:
                    game_state.shots.append(shot)

            weapon_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
            weapon_keys += [pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
            if event.key in weapon_keys:
                index = weapon_keys.index(event.key)
                if index < len(game_state.available_weapons):
                    game_state.blockshead.weapon = game_state.available_weapons[index]
                else:
                    print(f"Weapon {index} not available")
                #game_state.available_weapons
        # Pause controls
        if event.key == pygame.K_p:
            game_state.paused = not game_state.paused
            
    elif event.type == pygame.KEYUP:
        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            game_state.blockshead.x_vel = 0
            if game_state.blockshead.y_vel > 0:
                game_state.blockshead.direction = Direction.DOWN
            elif game_state.blockshead.y_vel != 0:
                game_state.blockshead.direction = Direction.UP

        elif event.key in [pygame.K_UP, pygame.K_DOWN]:
            game_state.blockshead.y_vel = 0
            if game_state.blockshead.x_vel > 0:
                game_state.blockshead.direction = Direction.RIGHT
            elif game_state.blockshead.x_vel != 0:
                game_state.blockshead.direction = Direction.LEFT
                
def draw_screen(window, characters, game_state, debug=True):
    """
    Draw characters and their debug circle
    """
    for c in characters:
        img = c.get_image()
        c_coords = c.get_coordinates()
        c_coords = c_coords[0] - game_state.offset_x,  c_coords[1] - game_state.offset_y
        x = c_coords[0] - img.get_width() // 2
        y = c_coords[1] - img.get_height() // 2
        window.blit(img, (x,y))

        if debug:
            x_hitbox_start = c_coords[0] - c.width // 2
            y_hitbox_start = c_coords[1] - c.height // 2
            x_hitbox_end = c.width
            y_hitbox_end = c.height
            pygame.draw.rect(window, (0,255,0), (x_hitbox_start, y_hitbox_start, x_hitbox_end, y_hitbox_end), 3)

def draw_shots(window, game_state):
    for s in game_state.shots:
        s.draw(window, game_state)
        
def update_weapons(game_config, game_state):
    new_weapons, new_ammo = [], dict()
    for weapon, threshold in game_config.weapons.items():
        if game_state.multiplier > threshold and weapon not in game_state.available_weapons:
            print(f"New weapon: {weapon}")
            game_state.messages.append((f"New weapon: {weapon}", 180))
            new_weapons.append(weapon)
            new_ammo[weapon] = game_config.ammo[weapon]
    
    return new_weapons, new_ammo

def update_ammo(game_config, game_state, multiplier=2.0, multiplier4=8.0):
    max_ammo = {w: a for w, a in game_config.ammo.items() if w in game_state.available_weapons}
    for weapon, threshold in game_config.weapons.items():
        if weapon in game_state.available_weapons and game_state.multiplier > threshold * multiplier:
            if type(max_ammo.get(weapon)) in [float, int]:
                max_ammo[weapon] = game_config.ammo[weapon] * 2
                if max_ammo[weapon] > game_state.max_ammo.get(weapon):
                    game_state.messages.append((f"{weapon}: Double ammo", 180))
        if weapon in game_state.available_weapons and game_state.multiplier > threshold * multiplier4:
            if type(max_ammo.get(weapon)) in [float, int]:
                max_ammo[weapon] = game_config.ammo[weapon] * 4
                if max_ammo[weapon] > game_state.max_ammo.get(weapon):
                    game_state.messages.append((f"{weapon}: Quad ammo", 180))

    return max_ammo

def draw_end_screen(game_state, window):
    window.fill(game_config.background_color)
    font = pygame.font.SysFont(None, 36)

    text1 = f"Game over!"
    img1 = font.render(text1, True, (100,100,100))
    window.blit(img1, (20, 20))

    text2 = f"Final Score: {math.ceil(game_state.score)}, Final Level: {game_state.level -1}"
    img2 = font.render(text2, True, (100,100,100))
    window.blit(img2, (20, 60))

    text3 = f"Press R to start a new game. Press any other key to quit"
    img3 = font.render(text3, True, (100,100,100))
    window.blit(img3, (20, 100))

def end_loop(game_state, window, clock):
    print("End loop")
    draw_end_screen(game_state, window)
    pygame.display.update()
    while True:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                return event.key == pygame.K_r

def main_loop(game_config, game_state, window, clock, levelup=False):
    game_config, game_state, window = new_level(game_config, game_state, window)
    
    for _ in range(2):
        wall = Fakewall(game_config)
        game_state.fakewalls.append(wall)
    
    fps = []
    #game_state.messages.append(("ebuns", 100))
    while True:
        if len(game_state.zombies) == 0 and game_state.level_zombies == 0:
            game_config, game_state, window = new_level(game_config, game_state, window)
        dt = clock.tick(60)
        fps = fps[-10:]
        fps.append(1000/ dt)

        title_str = f"blockshead – {np.mean(fps):.0f} fps"
        pygame.display.set_caption(title_str)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                handle_keys(event, window, game_config, game_state)

        if not game_state.paused:
            # Draw background
            window.fill(game_config.background_color)
            
            # Move characters
            game_state.blockshead.move(game_config, game_state)
            for zombie in game_state.devils + game_state.zombies:
                zombie.move(window, game_config, game_state)
                zombie.contact(game_state)

            # Calculate interactions, attacks
            for shot in game_state.shots:
                shot.update(game_config, game_state)

            for healthbox in game_state.healthboxes:
                healthbox.update(game_config, game_state)

            game_state.zombies = [z for z in game_state.zombies if z.health >= 1]
            game_state.devils = [z for z in game_state.devils if z.health >= 1]
            game_state.shots = [s for s in game_state.shots if s.lifetime >= 0]
            game_state.healthboxes = [b for b in game_state.healthboxes if b.active]
            game_state.blood_marks = [b for b in game_state.blood_marks if b.level_lifetime >= 0]
            game_state.multiplier = max(game_state.multiplier - game_config.multiplier_step, 1.0)
            new_weapons, new_ammo = update_weapons(game_config, game_state)
            game_state.available_weapons += new_weapons
            game_state.max_ammo = update_ammo(game_config, game_state)
            if len(new_weapons) >= 1:
                print("New weapons", new_weapons)
                for w in new_weapons:
                    game_state.blockshead.ammo_dict[w] = game_state.max_ammo[w]
                print(game_state.max_ammo)
            
            if np_choice([True, False], p=[game_config.zombie_spawn_rate, 1.0 - game_config.zombie_spawn_rate]):
                add_zombies(game_config, game_state, window)
            
            # Draw characters and objects
            # NOTE: Order matters here
            drawables = game_state.blood_marks + game_state.fakewalls + game_state.healthboxes
            drawables = drawables + [game_state.blockshead] + game_state.zombies + game_state.devils
            draw_screen(window, drawables, game_state)
            draw_stats(window, game_state, game_config)
            draw_shots(window, game_state)
            draw_messages(window, game_state, game_config)
            
            # Calculate map offset
            ## X-axis
            if game_state.blockshead.x - game_state.offset_x >= game_config.width * 0.8:
                game_state.offset_x = game_state.blockshead.x - game_config.width * 0.8
            elif game_state.blockshead.x - game_state.offset_x <= game_config.width * 0.2:
                game_state.offset_x = game_state.blockshead.x - game_config.width * 0.2
            ## Y-axis
            if game_state.blockshead.y - game_state.offset_y >= game_config.height * 0.8:
                game_state.offset_y = game_state.blockshead.y - game_config.height * 0.8
            elif game_state.blockshead.y - game_state.offset_y <= game_config.height * 0.2:
                game_state.offset_y = game_state.blockshead.y - game_config.height * 0.2
        else:
            draw_pause_screen(window, game_config)
        
        if game_state.blockshead.health <= 0:
            return
        
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    start_new_game = True
    while start_new_game:
        game_config, game_state, window = initialize_game()
        main_loop(game_config, game_state, window, clock)
        start_new_game = end_loop(game_state, window, clock)