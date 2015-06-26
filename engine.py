import random

import model
import settings


class GameOverException(Exception):
    pass


class PieceFactory:
    piece_specs = tuple(getattr(model.PieceSpecs, attr)
                        for attr in model.PieceSpecs.__dict__.keys() if not attr.startswith('_'))

    def __init__(self):
        self.bag = []

    def gen_piece(self):
        """
        Generate a new piece "randomly"
        The random generator generates pieces with the following algorithm:
            Randomly permute the sequence of all seven tetrominoes into a bag
            Deal each piece from this bag until empty, then repeat
        http://tetris.wikia.com/wiki/Random_Generator
        """
        if len(self.bag) == 0:
            self.bag = list(self.piece_specs)
            random.shuffle(self.bag)
        return model.Piece(*self.bag.pop())


class PieceController:

    def __init__(self, board):
        self.board = board
        self.piece_factory = PieceFactory()
        self.piece = None
        self.create_random_piece()

    def create_random_piece(self):
        self.piece = self.piece_factory.gen_piece()
        self.board.add_blocks(self.piece.blocks)

        # try to move new piece down into the starting position, on failure the player has a chance to move
        # the piece out of the way before getting a game over
        success = self.attempt_down_move()
        #if success:
        #    self.attempt_move_down()  # again depending on starting row (TODO: add as option)

    @staticmethod
    def rotate_matrix(matrix, k):
        """
        Rotate matrix k * 90 degrees clockwise
        """
        for i in range(k):
            matrix = list(zip(*matrix[::-1]))
        return matrix

    def attempt_rotate(self, k):
        """
        Attempt to rotate the current piece left (k=3) or right (k=1), returning True if successful
        """
        rotated = self.rotate_matrix(self.piece.matrix, k)
        iter_coords = model.Piece.iter_coords_from_matrix(rotated)
        new_coords = [(self.piece.r + r, self.piece.c + c) for r, c in iter_coords]
        success = self.board.attempt_update_blocks(self.piece.blocks, new_coords)
        if success:
            self.piece.matrix = rotated
        return success

    def attempt_rotate_left(self):
        return self.attempt_rotate(3)

    def attempt_rotate_right(self):
        return self.attempt_rotate(1)

    def attempt_side_move(self, c_delta):
        """
        Attempt to move the current piece left or right based on c_delta, returning True if successful
        """
        new_coordinates = [(block.r, block.c + c_delta) for block in self.piece.blocks]
        success = self.board.attempt_update_blocks(self.piece.blocks, new_coordinates)
        if success:
            self.piece.c += c_delta
        return success

    def attempt_down_move(self):
        """
        Attempt to move piece down one row, returning True if successful
        """
        new_coordinates = [(block.r + 1, block.c) for block in self.piece.blocks]
        success = self.board.attempt_update_blocks(self.piece.blocks, new_coordinates)
        if success:
            self.piece.r += 1
        return success

    def hard_drop(self):
        """
        Move current piece down repeatedly until it collides
        """
        while self.attempt_down_move():
            pass


class PhysicsEngine:

    def __init__(self, board, input_manager):
        self.board = board
        self.input_manager = input_manager
        self.controller = PieceController(self.board)

        # timing-related variables
        self.gravity_frame_wait = 60
        self.down_frame_wait = 0
        self.side_frame_wait = 0
        self.lock_frame_wait = None

    def step_one_frame(self):
        """
        Decide on piece movement for the current frame and decrement timing variables
        Called by App once per frame while the game state is set to 'running'
        """
        self.process_movement()
        self.gravity_frame_wait -= 1
        self.down_frame_wait -= 1
        self.side_frame_wait -= 1
        if self.lock_frame_wait is not None:
            self.lock_frame_wait -= 1

    def process_movement(self):
        """
        Check if it is time to move a piece and do so.

        TODO: refactor this mess
        """
        # check if lock in delay has triggered and expired
        if self.lock_frame_wait is not None and self.lock_frame_wait <= 0:
            self.lock_piece()
            self.lock_frame_wait = None
            return

        # check for side movement
        if self.input_manager.c_delta != 0 and self.side_frame_wait <= 0:
            moved = self.controller.attempt_side_move(self.input_manager.c_delta)
            if moved:
                self.lock_frame_wait = None  # reset lock delay
                # set delay based on autorepeat (initial or continuous)
                if not self.input_manager.auto_repeat:
                    self.side_frame_wait = settings.auto_repeat_initial_delay
                    self.input_manager.auto_repeat = True
                else:
                    self.side_frame_wait = settings.auto_repeat_delay

        # check for down movement
        if self.input_manager.down_pressed and self.down_frame_wait <= 0:
            moved = self.controller.attempt_down_move()
            if moved:
                self.down_frame_wait = settings.soft_drop_delay
                # reset lock delay and gravity
                self.lock_frame_wait = None
                self.gravity_frame_wait = 60
            else:
                if self.lock_frame_wait is None:
                    self.lock_frame_wait = settings.lock_delay  # trigger lock delay

        # check if its time to move from gravity
        if self.gravity_frame_wait <= 0:
            moved = self.controller.attempt_down_move()
            if not moved:
                if self.lock_frame_wait is None:
                    self.lock_frame_wait = settings.lock_delay
            self.gravity_frame_wait = 60

    def lock_piece(self):
        """
        Lock current piece at its current board position and get a new piece
        Raises GameOver exception
        """
        self.board.clear_full_rows()
        if self.board.is_game_over():
            raise GameOverException
        self.controller.create_random_piece()  # create piece THEN place on board ?

    def hard_drop(self):
        """
        Perform a hard drop then lock the current piece
        """
        self.controller.hard_drop()
        self.lock_piece()
        self.lock_frame_wait = None

    def rotate_left(self):
        success = self.controller.attempt_rotate_left()
        if success:
            self.lock_frame_wait = None

    def rotate_right(self):
        success = self.controller.attempt_rotate_right()
        if success:
            self.lock_frame_wait = None
