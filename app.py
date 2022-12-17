from blockshead.gamestate import *
from blockshead.characters import Blockshead
from blockshead.objects import *
import pygame

def initialize_game():
    pygame.init()

    game_config = GameConfig(canvas=None, width=1000, height=750)
    screen = pygame.display.set_mode([game_config.width, game_config.height])

    return game_config, None, None, screen

def startgame(game_config, init_state, game_state, window):
    # TODO: implement
    pass

def pause_game(game_config, game_state):
    # TODO: implement
    if not game_state.paused:
        pass
    else:
        pass

def end_game(window, game_config, game_state):
    # TODO: print text
    end_text = 'Game Over!\nFinal Score: {}, Final Level: {}'.format(ceil(game_state.score), game_state.level -1)
    
def update_stats(game_config, game_state):
    # TODO: draw stats
    game_config.canvas.delete(game_config.stats)
    game_config.stats = game_config.canvas.create_text(230,52,text=score_board)

def new_level(game_config, game_state, window):
    """
    For every new level all of the Devils and Zombies have been killed so new ones need to be created.
    Each time 70% more Zombies are added
    """
    # TODO: rewrite

    return game_config, game_state

def handle_keys(event, blockshead):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            blockshead.x_vel = -1
            blockshead.direction = Direction.LEFT
        if event.key == pygame.K_RIGHT:
            blockshead.x_vel = 1
            blockshead.direction = Direction.RIGHT
        if event.key == pygame.K_UP:
            blockshead.y_vel = -1
            blockshead.direction = Direction.UP
        if event.key == pygame.K_DOWN:
            blockshead.y_vel = 1
            blockshead.direction = Direction.DOWN
    elif event.type == pygame.KEYUP:
        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            blockshead.x_vel = 0
        elif event.key in [pygame.K_UP, pygame.K_DOWN]:
            blockshead.y_vel = 0
            

def draw_screen(window, characters):
    for c in characters:
        img = c.get_image()
        window.blit(img, c.get_coordinates())
    pass

def main_loop(game_config, init_state, game_state, window, blockshead, clock, levelup=False):
    
    while True:
        # Background
        window.fill(game_config.background_color)
        dt = clock.tick(60)
        #print(dt)
        # TODO: write logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                handle_keys(event, blockshead)

        blockshead.move(game_config)
        draw_screen(window, [blockshead])
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game_config, init_state, game_state, window = initialize_game()
    blockshead = Blockshead(game_config)
    main_loop(game_config, init_state, game_state, window, blockshead, clock)