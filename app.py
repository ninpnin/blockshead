from blockshead.gamestate import *
from blockshead.characters import Blockshead
from blockshead.objects import *
import pygame

def initialize_game():
    pygame.init()

    game_config = GameConfig(canvas=None, width=1000, height=750)
    screen = pygame.display.set_mode([game_config.width, game_config.height])

    # Background
    screen.fill(game_config.background_color)
    """
    window = WindowProperties(height=750, width=1000, x_buffer=40, y_buffer=40)
    window.x_start = 2 * window.x_buffer - 20
    window.y_start = 3 * window.y_buffer - 35
    window.x_end = window.width - window.x_buffer - 20
    window.y_end = window.height - window.y_buffer - 20
    
    canvas = tk.Canvas(highlightthickness=0, height=window.height, width=window.width)
    canvas.master.title("Blockshead")
    canvas.pack()
    
    
    init_state = InitState()
    game_state = GameState()
    """
    # Background
    """
    background = canvas.create_rectangle(0, 0, window.width, window.height, fill=game_config.background_color, belowThis=None)
    game_config.background = background
    """
    # Blockshead
    #game_state.blockshead = Blockshead(pygame.display, game_config)
    #game_state.stats = None
    
    # Borders
    """
    canvas.create_rectangle(0,0,(window.x_buffer),(window.y_buffer+window.height), fill="Black") # create all of the buffer images
    canvas.create_rectangle((window.x_buffer+window.width),0,(window.width-(window.x_buffer)),((2*window.y_buffer)+window.height), fill="Black")
    canvas.create_rectangle(0,0,(window.width-window.x_buffer),window.y_buffer, fill="Black")
    canvas.create_rectangle(0,(window.height-window.y_buffer),window.width,window.height, fill="Black")
    """

    # Start screen
    """
    init_state.startscreen = canvas.create_rectangle(0, 0, window.width, window.height, fill=game_config.background_color, belowThis=None)
    init_state.starttext = canvas.create_text(window.width // 2, window.height // 2, text="Start game by pressing 'G'", fill="Black", font=game_config.font)
    """

    # Pause screen
    """
    game_config.pausescreen = canvas.create_rectangle(0, 0, window.width, window.height, fill="#EBDCC7", aboveThis=None)
    game_config.pausetext = canvas.create_text(window.width // 2, window.height // 2, text="Paused", fill="Black", font=game_config.font)
    canvas.itemconfigure(game_config.pausescreen, state='hidden')
    canvas.itemconfigure(game_config.pausetext, state='hidden')
    """

    # Stats
    """
    game_config.stats = canvas.create_text(200,65)
    canvas.create_rectangle(window.x_buffer,window.y_buffer,window.width - window.x_buffer,window.y_buffer+20,fill="Red")
    """

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

def draw_screen(window, characters):
    for c in characters:
        img = c.get_image()
        window.blit(img, (c.x, c.y))
    pass

def main_loop(game_config, init_state, game_state, window, blockshead, clock, levelup=False):
    
    while True:
        dt = clock.tick(60)
        print(dt)
        # TODO: write logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        draw_screen(window, [blockshead])
        pygame.display.update()
        

if __name__ == "__main__":
    clock = pygame.time.Clock()
    game_config, init_state, game_state, window = initialize_game()
    blockshead = Blockshead(game_config)
    main_loop(game_config, init_state, game_state, window, blockshead, clock)