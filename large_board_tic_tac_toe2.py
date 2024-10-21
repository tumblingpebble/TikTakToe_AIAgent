import pygame
import numpy as np
import pygame_menu
from GameStatus_51202 import GameStatus
from multiAgents2 import minimax, negamax
import sys
import time
import logging

# Set up logging
logging.basicConfig(
    filename='game_log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(message)s'
)

class TicTacToeGame:
    """
    A class to represent the Tic Tac Toe game with support for multiple grid sizes (3x3 to 10x10), player vs computer, player vs player modes, and stylings
    """
    def __init__(self, size=(600, 600)):
        """
        Initializes the pygame, audio, game window, board state, and sets up the game variables such as colors, grid size, game mode, player symbol, and score.
        """
        #initializr pygame and mixer for audio
        pygame.init()
        pygame.mixer.init()

        #Audio files 
        self.ui_background_music = 'sounds/ui_background_music.wav'
        self.gameplay_background_music = 'sounds/gameplay_background_music.wav'
        self.hover_sound = 'sounds/hover_sound.wav'
        self.click_sound = 'sounds/click_sound.wav'
        self.symbol_placed_sound = 'sounds/symbol_placed_sound.wav'

        #Initialize screen size
        self.size = self.width, self.height = size

        #preload sounds with mixer
        self.hover_sound_effect = pygame.mixer.Sound(self.hover_sound)
        self.click_sound_effect = pygame.mixer.Sound(self.click_sound)
        self.symbol_placed_sound_effect = pygame.mixer.Sound(self.symbol_placed_sound)

        #Start UI music loop -1 for infinite loop
        pygame.mixer.music.load(self.ui_background_music)
        pygame.mixer.music.play(-1)

        # Define colors (neon theme)
        self.BLACK = (20, 20, 20)
        self.WHITE = (255, 255, 255)
        self.NEON_PINK = (255, 20, 147)
        self.NEON_BLUE = (0, 191, 255)
        self.NEON_GREEN = (50, 205, 50)
        self.NEON_ORANGE= (255,165, 0)
        self.GRID_COLOR = (50, 50, 50)
        self.BACKGROUND_COLOR = self.BLACK
        self.LINE_COLOR = self.GRID_COLOR
        self.CROSS_COLOR = self.NEON_PINK #Player X Symbol
        self.CIRCLE_COLOR = self.NEON_BLUE #Player O Symbol

        # Game settings
        self.GRID_SIZE = 3  # Default grid size (3x3)
        self.game_mode = 'Player vs Computer'  # Default game mode
        self.player_symbol = 'X'  # default players symbol
        self.ai_symbol = 'O'
        self.score = {'Player 1': 0, 'Player 2': 0, 'Draws': 0}
        self.algorithm = 'Minimax'  # Default algorithm

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Tic Tac Toe") #Set window title
        self.clock = pygame.time.Clock() # Control game frame rate

        self.menu = None  # Menu initialized later
        self.board_state = None #placeholder for the game board state
        self.game_state = None #track current game state (player turns, win state)
        self.game_over = False #game over flag

    def play_hover_sound(self):
            self.hover_sound_effect.play()#play hover sound over buttons

    def play_click_sound(self):
            self.click_sound_effect.play() #click sound for buttons
        
    def play_symbol_placement_sound(self):
            self.symbol_placed_sound_effect.play() #play when symbol on the grid

    def switch_to_gameplay_music(self):
            #switch to gameblack background music looo when starting game
            pygame.mixer.music.stop() #end UI music
            pygame.mixer.music.load(self.gameplay_background_music)
            pygame.mixer.music.play(-1) #play gameplay music in loop 
    
    def switch_to_ui_music(self):
            #switch back to UI music when game ends
            pygame.mixer.music.stop() #stop playing gameplay music
            pygame.mixer.music.load(self.ui_background_music)
            pygame.mixer.music.play(-1) #loop UI music
             
    def set_grid_size(self, value, grid_size):
        """
        Set the grid size of the game based on the player's choice from the menu.
        """
        self.GRID_SIZE = grid_size

    def set_game_mode(self, value, mode):
        """
        Set the game mode (Player vs Player or Player vs Computer).
        """
        self.game_mode = mode

    def set_algorithm(self, value, algorithm):
        """
        Set the algorithm used by the AI agent (Minimax or Negamax).
        """
        self.algorithm = algorithm.lower()

    def set_player_symbol(self, value, symbol):
        self.player_symbol = symbol
        self.ai_symbol = 'O' if symbol == 'X' else 'X'

    def start_game(self):
        """
        Stars the game by initializing board state and entering main game loop
        
        """
        self.switch_to_gameplay_music() #switch to gameplay music
        #Create empty board with zeros
        self.board_state = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        # Initialize GameStatus, 'O' always starts first in Tic Tac Toe
        self.game_state = GameStatus(self.board_state, turn_O=(self.player_symbol == 'O'))
        self.game_over = False # Reset the game over flag
        self.move_count = 1 #initialize move count
        #log start of new game
        logging.info(f"## New Game Started: {self.GRID_SIZE}x{self.GRID_SIZE} Grid, Mode: {self.game_mode}, Algorithm: {self.algorithm.capitalize()}")
        self.main_loop()

    def handle_hover(self, widget, menu):
        """Check if mouse is hovering over a button and play hover sound."""
        if widget.is_selected():
            self.play_hover_sound()

    def handle_click(self, event, button_rect):
        """Check if mouse clicks a button and play click sound."""
        if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            self.play_click_sound()  # Play click sound on button press
            # Handle the button click action...

    def main_menu(self):
        """
        Sets up the main menu using pygame_menu, allowing the player to choose grid size, game mode, and symbol.
        """
        background_image = pygame.image.load('UI_background.jpg')
        background_image = pygame.transform.scale(background_image, (self.width, self.height))
        #function to draw backgroudn image
        def draw_background():
            self.screen.blit(background_image, (0, 0))

            #Font for displaying score
            font = pygame.font.Font(pygame_menu.font.FONT_8BIT, 14)

            #score text
            score_text = f"Player 1  :  {self.score['Player 1']}  |  Player 2  :  {self.score['Player 2']}  |  Draws  :  {self.score['Draws']}"
            text = font.render(score_text, True, self.WHITE)

            #position near top of screen
            self.screen.blit(text, (self.width // 2 - text.get_width() / 2, 20))

        # Create the selection effect
        highlight_selection = pygame_menu.widgets.HighlightSelection(
            border_width=1
        )

        # Set margins using margin_xy
        highlight_selection.margin_xy(x=5, y=5)
        screen_width = self.width
        base_font_size = 48
        scaling_factor = screen_width / 1920
        adjusted_font_size = int(base_font_size * scaling_factor)

        # Use the selection effect in the theme
        theme = pygame_menu.themes.Theme(
            background_color=(0, 0, 0, 0),  # Fully transparent background
            title=False,
            widget_font=pygame_menu.font.FONT_8BIT,
            widget_font_size=adjusted_font_size,
            widget_font_color=self.WHITE,
            selection_color=self.NEON_PINK,
            widget_alignment=pygame_menu.locals.ALIGN_CENTER,
            widget_selection_effect=highlight_selection
        )

        # Create menu with custom theme
        self.menu = pygame_menu.Menu(
            title='',
            height=self.height,
            width=self.width,
            theme=theme,
            mouse_motion_selection=True
        )

        # Add options (Grid Size, Game Mode, Player Symbol, Algorithm)
        self.menu.add.selector('Grid Size :', [(f'{i}x{i}', i) for i in range(3, 11)], onchange=self.set_grid_size, padding=(10,10))
        self.menu.add.selector('Game Mode :', [('Player vs Computer', 'Player vs Computer'), ('Player vs Player', 'Player vs Player')], onchange=self.set_game_mode, padding=(10,10))
        self.menu.add.selector('Your Symbol :', [('X', 'X'), ('O', 'O')], onchange=self.set_player_symbol, padding=(10,10))
        self.menu.add.selector('Algorithm :', [('Minimax', 'minimax'), ('Negamax', 'negamax')], onchange=self.set_algorithm, padding=(10,10))


        self.menu.center_content()

        # Add buttons
        start_button = self.menu.add.button('Start Game', self.start_game)
        quit_button = self.menu.add.button('Quit', pygame_menu.events.EXIT)

        # Customize start button
        start_button.set_font(
            font=pygame_menu.font.FONT_8BIT,
            font_size=adjusted_font_size,
            color=self.WHITE,
            selected_color=(0,0,0), #hover black
            readonly_color=self.WHITE,
            readonly_selected_color=(0,0,0),
            background_color=None
        )

        #customize quit button to hover black
        quit_button.set_font(
            font=pygame_menu.font.FONT_8BIT,
            font_size=adjusted_font_size,
            color=self.WHITE,
            selected_color=(0,0,0), #hover black
            readonly_color=self.WHITE,
            readonly_selected_color=(0,0,0),
            background_color=None
        )

        # Set up sounds
        sound = pygame_menu.sound.Sound()
        sound.set_sound(pygame_menu.sound.SOUND_TYPE_WIDGET_SELECTION, self.hover_sound)
        sound.set_sound(pygame_menu.sound.SOUND_TYPE_CLICK_MOUSE, self.click_sound)
        self.menu.set_sound(sound, recursive=True)

        # Run the menu with the background function
        self.menu.mainloop(self.screen, bgfun=draw_background)

    def draw_board(self):
        """
        Draws the TicTacToe grid and sets up the background image for the UI.  The grid size can vary based on theh player's selctions
        """
        # Load and scale background image
        background_image = pygame.image.load('background.jpg')
        background_image = pygame.transform.scale(background_image, (self.width, self.height))
        self.screen.blit(background_image, (0, 0))

        grid_size = self.GRID_SIZE #Determine grid size
        cell_size = self.width / grid_size #calculate size of each cell

        # Draw grid lines
        for i in range(1, grid_size):
            pygame.draw.line(self.screen, self.LINE_COLOR, (i * cell_size, 0), (i * cell_size, self.height), 2)
            pygame.draw.line(self.screen, self.LINE_COLOR, (0, i * cell_size), (self.width, i * cell_size), 2)

    def draw_symbols(self):
        grid_size = self.GRID_SIZE
        cell_size = self.width / grid_size
        for i in range(grid_size):
            for j in range(grid_size):
                x = j * cell_size
                y = i * cell_size
                if self.board_state[i, j] == 1:
                    # Draw 'O'
                    center = (x + cell_size / 2, y + cell_size / 2)
                    radius = cell_size / 3
                    pygame.draw.circle(self.screen, self.CIRCLE_COLOR, center, radius, 20)
                elif self.board_state[i, j] == -1:
                    # Draw 'X'
                    start_pos = (x + cell_size / 5, y + cell_size / 5)
                    end_pos = (x + cell_size - cell_size / 5, y + cell_size - cell_size / 5)
                    pygame.draw.line(self.screen, self.CROSS_COLOR, start_pos, end_pos, 20)
                    start_pos = (x + cell_size - cell_size / 5, y + cell_size / 5)
                    end_pos = (x + cell_size / 5, y + cell_size - cell_size / 5)
                    pygame.draw.line(self.screen, self.CROSS_COLOR, start_pos, end_pos, 20)

    def check_game_over(self):
        if self.game_state.is_terminal():
            self.game_over = True
            self.update_score()
            self.display_winner()

    def update_score(self):
        if self.game_state.winner == 'Draw':
            self.score['Draws'] += 1
        elif self.game_mode == 'Player vs Computer':
            if self.game_state.winner == self.player_symbol:
                self.score['Player 1'] += 1
            else:
                self.score['Player 2'] += 1
        else:
            # Player vs Player mode
            current_player = 'Player 1' if self.game_state.winner == self.player_symbol else 'Player 2'
            self.score[current_player] += 1

    def display_winner(self):
        font = pygame.font.Font(None, 120)
        colors = [self.NEON_PINK, self.NEON_BLUE, self.NEON_GREEN, self.NEON_ORANGE]
        if self.game_state.winner == 'Draw':
            message = 'Draw!'
        else:
            message = f'{self.game_state.winner} Wins!'

        for _ in range(3):
            for color in colors:
                text = font.render(message, True, color)
                text_rect = text.get_rect(center=(self.width / 2, self.height / 2))
                self.screen.fill(self.BACKGROUND_COLOR)
                self.screen.blit(text, text_rect)
                pygame.display.update()
                time.sleep(0.5 / len(colors))
        
        #keep the message on the screen for 2 seconds
        text = font.render(message, True, self.WHITE)
        text_rect = text.get_rect(center=(self.width / 2, self.height / 2))
        self.screen.blit(text, text_rect)
        pygame.display.update()

        if self.game_state.winner != 'Draw':
            logging.info(f"Game over: {self.game_state.winner}!\n")
        else:
            logging.info("Game over: It's a draw!\n")

    def display_score(self):
        """
        Displays the triplet counts for each player on the game screen.
        """
        if self.GRID_SIZE > 3:
            font = pygame.font.Font(None, 36)  # Set font for score display
        
            # Get triplet counts
            O_triplets = self.game_state.count_triplets(1)
            X_triplets = self.game_state.count_triplets(-1)
            
            # Prepare the triplet counts text
            triplet_text = f"Triplets - O: {O_triplets} | X: {X_triplets}"
            text = font.render(triplet_text, True, self.WHITE)
            text_rect = text.get_rect(center=(self.width / 2, self.height - 20))  # Position at bottom of screen
            self.screen.blit(text, text_rect)

    def animate_move(self, row, col, symbol):
        """
        Animates placement of symbol and plays sound effect
        """
        #play placement sound
        self.play_symbol_placement_sound()
        
        grid_size = self.GRID_SIZE
        cell_size = self.width / grid_size
        x = col * cell_size
        y = row * cell_size


        if symbol == 'O':
            center = (x + cell_size / 2, y + cell_size / 2)
            radius = cell_size / 3
            for r in range(0, int(radius), 5):
                self.draw_board()
                self.draw_symbols()
                pygame.draw.circle(self.screen, self.CIRCLE_COLOR, center, r, 5)
                pygame.display.update()
                pygame.time.delay(20)
        elif symbol == 'X':
            for i in range(0, int(cell_size / 2), 5):
                self.draw_board()
                self.draw_symbols()
                start_pos1 = (x + i, y + i)
                end_pos1 = (x + cell_size - i, y + cell_size - i)
                pygame.draw.line(self.screen, self.CROSS_COLOR, start_pos1, end_pos1, 5)

                start_pos2 = (x + cell_size - i, y + i)
                end_pos2 = (x + i, y + cell_size - i)
                pygame.draw.line(self.screen, self.CROSS_COLOR, start_pos2, end_pos2, 5)
                pygame.display.update()
                pygame.time.delay(20)

    def main_loop(self):
        self.draw_board()
        self.draw_symbols()
        self.display_score()
        pygame.display.update()
        
        #initialize current_symbol based on turn 
        current_symbol = 'O' if self.game_state.turn_O else 'X'

        while True:
            self.clock.tick(30)

            if self.game_over:
                self.switch_to_ui_music() #switch back to UI music when game ends
                self.main_menu()
                break

            #event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    pos = pygame.mouse.get_pos()
                    grid_size = self.GRID_SIZE
                    cell_size = self.width / grid_size
                    row = int(pos[1] // cell_size)
                    col = int(pos[0] // cell_size)


                    if self.board_state[row, col] == 0: #check if cell is empty
                        self.player_move(row, col, current_symbol)
                        self.check_game_over()
                        if self.game_over:
                            break
                        else:
                            current_symbol = self.ai_symbol

            if not self.game_over and self.game_mode == 'Player vs Computer' and current_symbol == self.ai_symbol:
                #AI's turn
                self.ai_move(current_symbol)
                self.check_game_over()
                if self.game_over:
                    break
                current_symbol = self.player_symbol
            
            pygame.display.update()

    def evaluate_board(self):
        board = self.board_state
        size = board.shape[0]
        score = 0

        lines = []

        # Rows and columns
        for i in range(size):
            lines.append(board[i, :])  # Row
            lines.append(board[:, i])  # Column

        # Diagonals
        diag1 = np.array([board[i, i] for i in range(size)])
        diag2 = np.array([board[i, size - i - 1] for i in range(size)])
        lines.append(diag1)
        lines.append(diag2)

        for line in lines:
            score += self.evaluate_line(line)
        return score
    
    def format_board(self, board):
        size = board.shape[0]
        board_str = ''
        for i in range(size):
            row = ''
            for j in range(size):
                cell = board[i, j]
                if cell == 1:
                    row += 'O '
                elif cell == -1:
                    row += 'X '
                else:
                    row += '. '
            board_str += row.strip() + '\n'
        return board_str.strip()

    def evaluate_line(self, line):
        score = 0
        # Scoring for 'O'
        if np.count_nonzero(line == 1) == 3:
            score += 100
        elif np.count_nonzero(line == 1) == 2 and np.count_nonzero(line == 0) == 1:
            score += 10
        elif np.count_nonzero(line == 1) == 1 and np.count_nonzero(line == 0) == 2:
            score += 1

        # Scoring for 'X'
        if np.count_nonzero(line == -1) == 3:
            score -= 100
        elif np.count_nonzero(line == -1) == 2 and np.count_nonzero(line == 0) == 1:
            score -= 10
        elif np.count_nonzero(line == -1) == 1 and np.count_nonzero(line == 0) == 2:
            score -= 1
        return score

    
    def player_move(self, row, col, current_symbol):
        """
        handle players move, place symbol and update game state
        """
        self.board_state[row, col] = 1 if current_symbol == 'O' else -1
        self.game_state = self.game_state.get_new_state((row, col))
        self.animate_move(row, col, current_symbol)
        self.draw_symbols()
        self.display_score()
        pygame.display.update()

        #log the move
        logging.info(f"Player '{current_symbol}' placed at position ({row}, {col}).")
        logging.info(f"**Board state after the move:**\n```\n{self.format_board(self.board_state)}\n```\n")

    def ai_move(self, current_symbol):
        # Adjust depth based on grid size
        if self.GRID_SIZE == 3:
            depth = 9  # Full depth for perfect play
        elif self.GRID_SIZE == 4:
            depth = 7
        elif self.GRID_SIZE == 5:
            depth = 4
        elif self.GRID_SIZE == 6:
            depth = 3
        else:
            #for larger grids >= 7x7 adjust depth based on remaining moves
            empty_cells = np.count_nonzero(self.board_state == 0)
            total_cells = self.GRID_SIZE * self.GRID_SIZE

            #calculate percentage of the board thats empty
            empty_ratio = empty_cells / total_cells

            #adjust depth based on empty cells
            if empty_ratio > 0.8:
                depth = 2
            elif empty_ratio > 0.4:
                depth = 3
            elif empty_ratio > 0.25:
                depth = 4
            else:
                depth = 5 #endgame depth
        
        #set color based on AI's symbol
        color = 1 if self.ai_symbol == 'O' else -1

        # Choose the algorithm based on the player's selection
        if self.algorithm == 'minimax':
            score, move = minimax(self.game_state, depth, True)
        elif self.algorithm == 'negamax':
            score, move = negamax(self.game_state, depth, color)
        else:
        # Default to minimax if for some reason the algorithm is not recognized
            score, move = minimax(self.game_state, depth, True)
        if move:
            row, col = move
            self.board_state[row, col] = 1 if current_symbol == 'O' else -1
            self.game_state = self.game_state.get_new_state((row, col))
            self.animate_move(row, col, current_symbol)
            self.draw_symbols()
            self.display_score()
            pygame.display.update()

            #log AI's move
            logging.info(f"AI '{current_symbol}' placed at position ({row}, {col}).")
            logging.info(f"Algorithm used: {self.algorithm.capitalize()}")  # Log the algorithm used
            logging.info(f"AI evaluated move with score: {score}")
            logging.info(f"**Board state after AI's move:**\n```\n{self.format_board(self.board_state)}\n```\n")

            
if __name__ == '__main__':
    game = TicTacToeGame()
    game.main_menu()