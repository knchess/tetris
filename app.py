from enum import Enum

import pygame

import engine
import model
import settings
import view


class InputManager:
    """
    Manages input state related to movement
    InputManager will receive movement-related keydown and keyup events from the App
    The PhysicsEngine will use the input state to make decisions about moving the current piece
    """

    def __init__(self):
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.c_delta = 0
        self.auto_repeat = False  # flag whether side movements should move at autorepeat speed (or wait for delay)

    def keydown(self, key):
        if key == pygame.K_LEFT:
            self.left_pressed = True
            self.c_delta = -1
        elif key == pygame.K_RIGHT:
            self.right_pressed = True
            self.c_delta = 1
        elif key == pygame.K_DOWN:
            self.down_pressed = True

    def keyup(self, key):
        if key == pygame.K_LEFT:
            self.left_pressed = False
            self.c_delta = 0
            self.auto_repeat = False
            if self.right_pressed:
                self.c_delta = 1
        elif key == pygame.K_RIGHT:
            self.right_pressed = False
            self.c_delta = 0
            self.auto_repeat = False
            if self.left_pressed:
                self.c_delta = -1
        elif key == pygame.K_DOWN:
            self.down_pressed = False


class GameState(Enum):
    initialized = 0
    running = 1
    paused = 2
    game_over = 3
    reset = 4
    quit = 5


class App:

    def __init__(self):
        """
        Setup objects and initial state. Creates a Clock, Board, View, PhysicsEngine, and InputManager
        """
        pygame.init()
        self.clock = pygame.time.Clock()
        self.board = model.Board(settings.num_rows + 2, settings.num_cols)  # adding the two hidden rows
        self.view = view.View(self.board, settings.block_width, settings.hidden_row_fraction)
        self.input_manager = InputManager()
        self.engine = engine.PhysicsEngine(self.board, self.input_manager)
        self.game_state = GameState.initialized

    def reset(self):
        """
        Start a new game by resetting board and engine
        """
        self.board.reset()
        self.engine = engine.PhysicsEngine(self.board, self.input_manager)
        self.game_state = GameState.running

    def run(self):
        """
        Run the game through a main loop. Each iteration of the loop corresponds to one frame (60 frames per second)
        A piece can move at most once per frame. However, the number of cells the piece moves
        depends on current state of input and speed settings
        """
        self.game_state = GameState.running
        while self.game_state != GameState.quit:  # run until a quit event
            if self.game_state == GameState.reset:
                self.reset()
            self.process_frame()
        pygame.quit()

    def process_frame(self):
        """
        Process events, process movement, update the display and then step forward one frame
        """
        try:
            self.process_events()
            if self.game_state == GameState.running:
                self.engine.step_one_frame()
        except engine.GameOverException:  # TODO: remove
            self.game_state = GameState.game_over
        self.update_display()
        self.clock.tick(60)  # wait for frame end (at 60 fps)

    def process_events(self):
        """
        Process relevant PyGame events (key inputs and quit request)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.quit
            elif event.type == pygame.KEYDOWN:
                self.process_keydown(event.key)
            elif event.type == pygame.KEYUP:
                self.input_manager.keyup(event.key)

    def process_keydown(self, key):
        """
        Process keydown event
        Pause/resume, and reset are handled directly
        Movement related events are sent to input_manager
        The engine is called for rotations or hard drop, if the game is not paused
        """
        if key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self.game_state == GameState.game_over:
                self.game_state = GameState.reset

        elif key == pygame.K_p:
            self.toggle_pause()

        elif key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]:
            self.input_manager.keydown(key)  # forward movement events

        # only handle following events if game is not paused
        if self.game_state != GameState.running:
            return

        if key == pygame.K_SPACE:
            self.engine.hard_drop()

        elif key in [pygame.K_UP, pygame.K_x]:
            self.engine.rotate_right()
        elif key == pygame.K_z:
            self.engine.rotate_left()

    def toggle_pause(self):
        """
        Toggle game state between paused/running.
        If the game state is not paused or running (e.g. game over), then do nothing
        """
        if self.game_state == GameState.paused:
            self.game_state = GameState.running
        elif self.game_state == GameState.running:
            self.game_state = GameState.paused

    def update_display(self):
        """
        Draw all elements of the game.
        """
        self.view.draw_board()
        if self.game_state == GameState.game_over:
            self.view.display_game_over_dialog()
        if self.game_state == GameState.paused:
            self.view.display_pause_dialog()
        pygame.display.flip()
