import pygame


class Colors:
    """
    Class for getting RGB values from a color name
    Names and values are based on CSS3
    """
    black = (0, 0, 0)
    white = (255, 255, 255)
    lightgray = (211, 211, 211)
    blueviolet = (138, 43, 226)
    cyan = (0, 255, 255)
    dodgerblue = (30, 144, 255)
    darkorange = (255, 140, 0)
    limegreen = (50, 205, 50)
    red = (255, 0, 0)
    yellow = (255, 255, 0)


class View:
    """
    Class for handling display of all elements to the PyGame screen
    """

    def __init__(self, board, block_width, hidden_row_fraction):
        self.board = board

        self.block_width = block_width
        self.hidden_row_offset = int(hidden_row_fraction * self.block_width)

        # the +1 offset is to needed to make grid lines appear on the bottom and right sides
        self.window_size = (self.board.num_cols * self.block_width + 1,
                            (self.board.num_rows - 2) * self.block_width + self.hidden_row_offset + 1)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Tetris")

    def draw_board(self):
        self.screen.fill(Colors.white)
        self.board.draw(self)

    def draw_horizontal_line(self, r):
        x = (r - 2) * self.block_width + self.hidden_row_offset
        pygame.draw.line(self.screen, Colors.lightgray, (0, x), (self.board.num_cols * self.block_width, x))

    def draw_vertical_line(self, c):
        y = c * self.block_width
        pygame.draw.line(self.screen, Colors.lightgray, (y, 0), (y, self.board.num_rows * self.block_width))

    def draw_block(self, block):
        width = self.block_width
        x = (block.r - 2) * width + self.hidden_row_offset
        y = block.c * width
        pygame.draw.rect(self.screen, block.color,
                         [y, x, width, width])
        pygame.draw.lines(self.screen, Colors.black, True,
                          [(y, x), (y, x + width),
                           (y + width, x + width), (y + width, x)], 1)

    def display_dialog(self, message, message2=None):
        """
        Display a dialog covering the grid
        message appears in size 30 Verdana
        if message2 is given, it appears below message in size 16 Verdana

        This method is currently inflexible but only used for displaying game over and pause messages
        TODO: refactor when adding control dialog (many lines)
        """
        centerx, centery = self.screen.get_rect().centerx, self.screen.get_rect().centery

        font = pygame.font.SysFont('Verdana', 30)
        text = font.render(message, True, Colors.black)
        text_pos = text.get_rect()
        text_pos.centerx = centerx
        text_pos.centery = centery // 2
        if message2 is not None:
            text_pos.centery -= 15
        box_width = text.get_width() + 20
        box_height = text.get_height() + 10

        if message2 is not None:
            font = pygame.font.SysFont('Verdana', 16)
            text2 = font.render(message2, True, Colors.black)
            text2_pos = text2.get_rect()
            text2_pos.centerx = centerx
            text2_pos.centery = centery // 2 + 15
            box_width = max(text.get_width(), text2.get_width()) + 20
            box_height += text2.get_height() + 10

        # create a white box to cover the grid
        box_size = (box_width, box_height)
        box = pygame.Surface(box_size)
        box_pos = box.get_rect()
        box_pos.centerx = centerx
        box_pos.centery = centery // 2
        box.fill(Colors.white)
        self.screen.blit(box, box_pos)

        pygame.draw.rect(self.screen, Colors.black, box_pos, 1)  # draw a border around the box
        self.screen.blit(text, text_pos)
        if message2 is not None:
            self.screen.blit(text2, text2_pos)

    def display_game_over_dialog(self):
        self.display_dialog("GAME OVER", "Press Enter to restart")

    def display_pause_dialog(self):
        self.display_dialog("PAUSED", "Press P to resume")
