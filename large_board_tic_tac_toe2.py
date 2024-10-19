import pygame
import numpy as np
import pygame_menu
from GameStatus_51202 import GameStatus
from multiAgents2 import minimax
import sys
import time

class TicTacToeGame:
    """
    A class to represent the Tic Tac Toe game with support for multiple grid sizes (3x3 to 10x10), player vs computer, player vs player modes, and stylings
    """
    def __init__(self, size=(600, 600)):
        """
        Initializes the game window, board state, and sets up the game variables such as colors, grid size, game mode, player symbol

        Args: size (tuple): The size of the game window
        """
        #Initialize screen size
        self.size = self.width, self.height = size

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
        self.player_symbol = 'O'  # default players symbol
        self.ai_symbol = 'X'
        self.score = {'Player 1': 0, 'Player 2': 0, 'Draws': 0}

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Tic Tac Toe") #Set window title
        self.clock = pygame.time.Clock() # Control game frame rate

        self.menu = None  # Menu initialized later
        self.board_state = None #placeholder for the game board state
        self.game_state = None #track current game state (player turns, win state)
        self.game_over = False #game over flag

    def set_grid_size(self, value, grid_size):
        """
        Set the grid size of the game based on the player's choice from the menu.
        
        Args:
            value: the internal value passed by pygame_menu(unused).
            grid_size (int): The selected grid size ( e.g., 3x3, 4x4, etc.)
        """
        self.GRID_SIZE = grid_size

    def set_game_mode(self, value, mode):
        """
        Set the game mode (Player vs Player or Player vs Computer).
        
        Args:
            value: the internal value passed by pygame_menu(unused).
            mode (str): The selected game mode (Player vs Player or Player vs Computer).
        """
        self.game_mode = mode

    def set_player_symbol(self, value, symbol):
        self.player_symbol = symbol
        self.ai_symbol = 'O' if symbol == 'X' else 'X'

    def start_game(self):
        """
        Stars the game by initializing board state and entering main game loop
        
        """
        #Create empty board with zeros
        self.board_state = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        # Initialize GameStatus, 'O' always starts first in Tic Tac Toe
        self.game_state = GameStatus(self.board_state, turn_O=True)
        self.game_over = False # Reset the game over flag
        self.main_loop()

    def main_menu(self):
        """
        Sets up the main menu using pygame_menu, allowing the player to choose grid size, game mode and symbol
        """
        #Create menu (dark theme) (need to edit to synthwave generic theme)
        self.menu = pygame_menu.Menu('Tic Tac Toe', self.width, self.height,
                                     theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.selector('Grid Size :', [(f'{i}x{i}', i) for i in range(3, 11)], onchange=self.set_grid_size)
        self.menu.add.selector('Game Mode :', [('Player vs Computer', 'Player vs Computer'), ('Player vs Player', 'Player vs Player')], onchange=self.set_game_mode)
        self.menu.add.selector('Your Symbol :', [('O', 'O'), ('X', 'X')], onchange=self.set_player_symbol)
        #Buttons to start the game or quit
        self.menu.add.button('Start Game', self.start_game)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        
        #Display the menu
        self.menu.mainloop(self.screen)

    def draw_board(self):
        """
        Draws the TicTacToe grid and sets up the background image for the UI.  The grid size can vary based on theh player's selctions
        """
        # Load and scale background image
        background_image = pygame.image.load('background.png')
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

    def display_score(self):
        font = pygame.font.Font(None, 30)
        score_text = f"Player 1: {self.score['Player 1']}  Player 2: {self.score['Player 2']}  Draws: {self.score['Draws']}"
        text = font.render(score_text, True, self.WHITE)
        self.screen.blit(text, (10, self.height - 30))

    def animate_move(self, row, col, symbol):
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

        current_symbol = 'O' if self.game_state.turn_O else 'X'
        while True:
            self.clock.tick(30)
            if self.game_over:
                self.main_menu()
                break

            if self.game_mode == 'Player vs Computer':
                if current_symbol == self.player_symbol:
                    # Player's turn
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                            pos = pygame.mouse.get_pos()
                            grid_size = self.GRID_SIZE
                            cell_size = self.width / grid_size
                            row = int(pos[1] // cell_size)
                            col = int(pos[0] // cell_size)
                            if self.board_state[row, col] == 0:
                                self.board_state[row, col] = 1 if current_symbol == 'O' else -1
                                self.game_state = self.game_state.get_new_state((row, col))
                                self.animate_move(row, col, current_symbol)
                                self.draw_symbols()
                                self.display_score()
                                pygame.display.update()
                                self.check_game_over()
                                if self.game_over:
                                    break
                                else:
                                    current_symbol = self.ai_symbol
                else:
                    # AI's turn
                    depth = len(self.game_state.get_moves())
                    maximizingPlayer = (current_symbol == 'O')
                    score, move = minimax(self.game_state, depth, maximizingPlayer)
                    if move:
                        row, col = move
                        self.board_state[row, col] = 1 if current_symbol == 'O' else -1
                        self.game_state = self.game_state.get_new_state((row, col))
                        self.animate_move(row, col, current_symbol)
                        self.draw_symbols()
                        self.display_score()
                        pygame.display.update()
                        self.check_game_over()
                        if self.game_over:
                            break
                        else:
                            current_symbol = self.player_symbol
            else:
                # Player vs Player mode
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                        pos = pygame.mouse.get_pos()
                        grid_size = self.GRID_SIZE
                        cell_size = self.width / grid_size
                        row = int(pos[1] // cell_size)
                        col = int(pos[0] // cell_size)
                        if self.board_state[row, col] == 0:
                            self.board_state[row, col] = 1 if current_symbol == 'O' else -1
                            self.game_state = self.game_state.get_new_state((row, col))
                            self.animate_move(row, col, current_symbol)
                            self.draw_symbols()
                            self.display_score()
                            pygame.display.update()
                            self.check_game_over()
                            if self.game_over:
                                break
                            else:
                                current_symbol = 'X' if current_symbol == 'O' else 'O'
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

if __name__ == '__main__':
    game = TicTacToeGame()
    game.main_menu()
