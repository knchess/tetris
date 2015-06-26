import settings
from view import Colors


class PieceSpecs:
    """
    Specifications for the shape and colour of each piece
    """

    I = ([[0, 0, 0, 0],
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]], Colors.cyan)
    J = ([[1, 0, 0],
          [1, 1, 1],
          [0, 0, 0]], Colors.dodgerblue)
    L = ([[0, 0, 1],
          [1, 1, 1],
          [0, 0, 0]], Colors.darkorange)
    O = ([[1, 1],
          [1, 1]], Colors.yellow)
    S = ([[0, 1, 1],
          [1, 1, 0],
          [0, 0, 0]], Colors.limegreen)
    T = ([[0, 1, 0],
          [1, 1, 1],
          [0, 0, 0]], Colors.blueviolet)
    Z = ([[1, 1, 0],
          [0, 1, 1],
          [0, 0, 0]], Colors.red)


class Block:

    def __init__(self, color, r, c):
        self.color = color
        self.r = r
        self.c = c


class Piece:

    def __init__(self, matrix, color):
        self.matrix = matrix
        self.color = color
        self.dimension = len(matrix[0])
        self.r = 0
        self.c = (settings.num_cols - self.dimension) // 2
        self.blocks = [Block(self.color, self.r + r, self.c + c)
                       for r, c in self.iter_coords_from_matrix(self.matrix)]

    @staticmethod
    def iter_coords_from_matrix(matrix):
        """
        Yield co-ordinates of non-zero entries of matrix
        """
        for r, row in enumerate(matrix):
            for c, element in enumerate(row):
                if element != 0:
                    yield r, c


class Board:

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.grid = []
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]

    def is_game_over(self):
        """
        Return True if a block is contained in the top two (hidden) rows.
        This indicates a game over once a piece is locked in.
        """
        for row in self.grid[:2]:
            for col in row:
                if col is not None:
                    return True
        return False

    def has_collision(self, coords):
        """
        Return False if each (r, c) pair in coordinates is free in the grid.
        (r, c) values outside of the legal grid range count as collisions.
        """
        for r, c in coords:
            if r >= self.num_rows or c >= self.num_cols or c < 0:  # bounds check
                return True
            if self.grid[r][c] is not None:
                return True
        return False

    def remove_blocks(self, blocks):
        for block in blocks:
            self.grid[block.r][block.c] = None

    def add_blocks(self, blocks):
        for block in blocks:
            self.grid[block.r][block.c] = block

    def attempt_update_blocks(self, blocks, new_coords):
        """
        Attempt to update the co-ordinates of blocks to new_coords
        The blocks are first removed from the grid, then a check is done to see if all new_coords are free
        If so, the coords of blocks are updated and re-added to the grid
        Otherwise, the blocks are re-added with the original co-ordinates
        """
        self.remove_blocks(blocks)
        if self.has_collision(new_coords):
            self.add_blocks(blocks)
            return False

        # update co-ordinates
        for block, (r, c) in zip(blocks, new_coords):
            self.grid[r][c] = block
            block.r, block.c = r, c
        return True

    def clear_full_rows(self):
        """
        Clear all full rows in the grid, moving all rows above a cleared row down one cell.
        """
        for i, row in enumerate(self.grid):
            has_empty_cell = False
            # determine if this row is full
            for col in row:
                if col is None:
                    has_empty_cell = True
                    break  # move to next row
            if not has_empty_cell:
                # full row; clear current row
                self.grid[i] = [None for _ in range(len(row))]
                # move each row above the cleared one down, starting from the bottommost row
                for j in range(i, 0, -1):
                    for block in self.grid[j]:
                        if block is not None:
                            self.grid[block.r][block.c] = None
                            block.r += 1
                            self.grid[block.r][block.c] = block
                self.grid[0] = [None for _ in range(self.num_cols)]  # add a new empty top row

    def draw(self, view):
        """
        Draw the grid onto the given View.
        """
        # draw grid lines
        for r in range(self.num_rows):
            view.draw_horizontal_line(r)
        for c in range(self.num_cols + 1):
            view.draw_vertical_line(c)

        # draw each block
        for row in self.grid:
            for block in row:
                if block is not None:
                    view.draw_block(block)
