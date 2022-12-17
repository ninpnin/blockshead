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
    
def draw_stats(window, game_state):
    font = pygame.font.SysFont(None, 36)
    img = font.render(f'Points: {game_state.score}', True, (100,100,100))
    window.blit(img, (20, 20))

def new_level(game_config, game_state, window):
    """
    For every new level all of the Devils and Zombies have been killed so new ones need to be created.
    Each time 70% more Zombies are added
    """
    
    game_state.zombies = []
    for _ in range(game_state.number_of_zombies):
        game_state.zombies.append(Zombie(window, game_config))
    # TODO: rewrite
    
    return game_config, game_state, window

    return game_config, game_state

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
                game_state.blockshead.fire_gun(window, game_config, game_state)

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
                
def draw_screen(window, characters):
    for c in characters:
        img = c.get_image()
        window.blit(img, c.get_coordinates())
    
def main_loop(game_config, game_state, window, clock, levelup=False):
    
    game_config, game_state, window = new_level(game_config, game_state, window)
    while True:
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
            game_state.blockshead.move(game_config)
            for zombie in game_state.zombies:
                zombie.move(window, game_config, game_state)
            
            # Draw characters and objects
            draw_screen(window, [game_state.blockshead] + game_state.zombies)
            draw_stats(window, game_state)
        else:
            draw_pause_screen(window, game_config)
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game_config, game_state, window = initialize_game()
    main_loop(game_config, game_state, window, clock)