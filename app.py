from blockshead.gamestate import *
from blockshead.characters import Blockshead, Zombie
from blockshead.objects import *
import pygame

def initialize_game():
    pygame.init()
    pygame.display.set_caption('Blockshead')
    game_config = GameConfig(canvas=None, width=1000, height=750)
    screen = pygame.display.set_mode([game_config.width, game_config.height])
    game_state = GameState()
    game_state.blockshead = Blockshead(game_config)
    return game_config, None, game_state, screen

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
    
    game_state.zombies = []
    for _ in range(game_state.number_of_zombies):
        game_state.zombies.append(Zombie(window, game_config))
    # TODO: rewrite
    
    return game_config, game_state, window

    return game_config, game_state

def handle_keys(event, window, game_config, game_state):
    if event.type == pygame.KEYDOWN:
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

    font = pygame.font.SysFont(None, 36)
    img = font.render('hello', True, (255,255,255))
    window.blit(img, (20, 20))
    
def main_loop(game_config, init_state, game_state, window, clock, levelup=False):
    
    game_config, game_state, window = new_level(game_config, game_state, window)
    while True:
        # Draw background
        window.fill(game_config.background_color)
        dt = clock.tick(60)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                handle_keys(event, window, game_config, game_state)

        # Move characters
        game_state.blockshead.move(game_config)
        for zombie in game_state.zombies:
            zombie.move(window, game_config, game_state)
        
        # Draw characters and objects
        draw_screen(window, [game_state.blockshead] + game_state.zombies)
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game_config, init_state, game_state, window = initialize_game()
    main_loop(game_config, init_state, game_state, window, clock)