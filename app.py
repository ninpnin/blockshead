from blockshead.gamestate import *
from blockshead.characters import Blockshead, Zombie
from blockshead.objects import *
import pygame
import math

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

def end_game(window, game_config, game_state):
    # TODO: print text
    end_text = f'Game Over!\nFinal Score: {math.ceil(game_state.score)}, Final Level: {game_state.level -1}'
    
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
    pygame.draw.rect(window, (255,0,0), (20 + game_state.blockshead.x, game_state.blockshead.y - 20, 100, 10))
    healthbar_width = int(100 * health/game_config.max_health)
    pygame.draw.rect(window, (0,128,0), (20 + game_state.blockshead.x, game_state.blockshead.y - 20, healthbar_width, 10))


def new_level(game_config, game_state, window):
    game_state.number_of_zombies += 1
    game_state.zombies = []
    while len(game_state.zombies) < game_state.number_of_zombies:
        zombie = Zombie(window, game_config)
        if not zombie._check_collisions(zombie.x, zombie.y, game_state, game_config):
            game_state.zombies.append(zombie)
    
    healthbox = Healthbox(game_config, game_state)
    game_state.healthboxes.append(healthbox)
    
    for blood_mark in game_state.blood_marks:
        blood_mark.levelup()
        
    game_state.level += 1
    
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
                
def draw_screen(window, characters, debug=True):
    for c in characters:
        img = c.get_image()
        c_coords = c.get_coordinates()
        x = c_coords[0] - img.get_width() // 2
        y = c_coords[1] - img.get_height() // 2
        window.blit(img, (x,y))

        if debug:
            pygame.draw.circle(window, (0,255,0), c_coords, c.radius, 3)

def draw_shots(window, game_state):
    for s in game_state.shots:
        s.draw(window)

def update_weapons(game_config, game_state):
    new_weapons, new_ammo = [], dict()
    for weapon, threshold in game_config.weapons.items():
        if game_state.multiplier > threshold and weapon not in game_state.available_weapons:
            print(f"New weapon: {weapon}")
            new_weapons.append(weapon)
            new_ammo[weapon] = game_config.ammo[weapon]
    
    return new_weapons, new_ammo
    
def main_loop(game_config, game_state, window, clock, levelup=False):
    game_config, game_state, window = new_level(game_config, game_state, window)
    
    for _ in range(2):
        wall = Fakewall(game_config)
        game_state.fakewalls.append(wall)
        
    while True:
        if len(game_state.zombies) == 0:
            game_config, game_state, window = new_level(game_config, game_state, window)
        dt = clock.tick(60)
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
            for zombie in game_state.zombies:
                zombie.move(window, game_config, game_state)
                zombie.contact(game_state)

            # Calculate interactions, attacks
            for shot in game_state.shots:
                shot.update(game_config, game_state)

            for healthbox in game_state.healthboxes:
                healthbox.update(game_config, game_state)

            game_state.zombies = [z for z in game_state.zombies if z.health >= 1]
            game_state.shots = [s for s in game_state.shots if s.lifetime >= 0]
            game_state.healthboxes = [b for b in game_state.healthboxes if b.active]
            game_state.blood_marks = [b for b in game_state.blood_marks if b.level_lifetime >= 0]
            game_state.multiplier = max(game_state.multiplier - game_config.multiplier_step, 1.0)
            new_weapons, new_ammo = update_weapons(game_config, game_state)
            game_state.available_weapons += new_weapons
            for weapon in new_weapons:
                game_state.blockshead.ammo_dict[weapon] = new_ammo[weapon]
            
            # Draw characters and objects
            # NOTE: Order matters here
            drawables = game_state.blood_marks + game_state.fakewalls + game_state.healthboxes
            drawables = drawables + [game_state.blockshead] + game_state.zombies
            draw_screen(window, drawables)
            draw_stats(window, game_state, game_config)
            draw_shots(window, game_state)
        else:
            draw_pause_screen(window, game_config)
        
        if game_state.blockshead.health <= 0:
            return
        
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game_config, game_state, window = initialize_game()
    main_loop(game_config, game_state, window, clock)