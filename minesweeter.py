from dataclasses import dataclass
import math
import pygame
import random


@dataclass
class Parameters:
    # game parameters
    bombs = 10
    columns = 9
    rows = 9

    id_air = 9
    id_bomb = 10

    # graphics parameters
    block_size = 100
    color_background = (192, 192, 192)
    color_flag = (128, 0, 64)
    color_hidden = (100, 100, 100, 200)
    color_line = (128, 128, 128)
    color_number = [
        None,
        (0, 0, 255),  # 1
        (0, 128, 0),  # 2
        (255, 0, 0),  # 3
        (0, 0, 128),  # 4
        (128, 0, 0),  # 5
        (0, 128, 128),  # 6
        (0, 0, 0),  # 7
        (128, 128, 128),  # 8
    ]
    font_size = math.ceil(0.8 * block_size)
    line_width = 15
    offset_h = block_size // 2
    offset_v = block_size + block_size // 2
    screen_height = block_size * 11
    screen_width = block_size * 10


class Board:
    def __init__(self, par):
        self.par = par
        self.board = [
            [self.par.id_air for _ in range(self.par.columns)]
            for _ in range(self.par.rows)
        ]
        self.is_visible = [
            [False for _ in range(self.par.columns)] for _ in range(self.par.rows)
        ]

    def __getitem__(self, row_col):
        row, col = self._row_col_valid(*row_col)
        if row is not None:
            return self.board[row][col]
        else:
            return self.par.id_air

    def __setitem__(self, row_col, val):
        row, col = self._row_col_valid(*row_col)
        if row is not None:
            self.board[row][col] = val

    def _row_col_valid(self, row, col):
        if 0 <= row and row < self.par.rows:
            if 0 <= col and col < self.par.columns:
                return row, col
        return None, None

    def init_board(self):
        # place bombs
        bomb_pos = random.sample(
            range(self.par.rows * self.par.columns), self.par.bombs
        )
        for b_p in bomb_pos:
            row = b_p // self.par.columns - 1
            col = b_p % self.par.columns
            self[row, col] = self.par.id_bomb

        # place bomb numbers
        for row in range(self.par.rows):
            for col in range(self.par.columns):
                if self[row, col] != self.par.id_air:
                    continue
                num_bombs = 0
                for i in range(-1, 2):
                    if self[row + i, col - 1] == self.par.id_bomb:
                        num_bombs += 1
                    if self[row + i, col + 1] == self.par.id_bomb:
                        num_bombs += 1
                if self[row - 1, col] == self.par.id_bomb:
                    num_bombs += 1
                if self[row + 1, col] == self.par.id_bomb:
                    num_bombs += 1
                if num_bombs > 0:
                    self[row, col] = num_bombs

    def mark_block(self, pos):
        if pos is None:
            return None
        row, col = pos
        if self.is_visible[row][col]:
            return None
        self[row, col] *= -1

    def open_block(self, pos):
        if pos is None:
            return None
        row, col = self._row_col_valid(*pos)
        if row is None:
            return None
        block = self[row, col]
        if block == self.par.id_bomb:
            print("you lose")
        else:
            if block > 0:
                self.is_visible[row][col] = True

    def click_block(self, pos):
        if pos is None:
            return None
        row, col = pos
        block = self[row, col]
        if block < 0:  # block is flagged
            return None
        else:
            self.open_block(pos)

            block = self[row, col]
            if self.is_visible[row][col]:
                if 0 < block < 9:
                    # count flags surrounding the block
                    num_flags = 0
                    for i in range(-1, 2):
                        if self[row + i, col - 1] < 0:
                            num_flags += 1
                        if self[row + i, col + 1] < 0:
                            num_flags += 1
                    if self[row - 1, col] < 0:
                        num_flags += 1
                    if self[row + 1, col] < 0:
                        num_flags += 1

                    # unveil all surrounding blocks
                    if num_flags == block:
                        for i in range(-1, 2):
                            self.open_block((row + i, col - 1))
                            self.open_block((row + i, col + 1))
                        self.open_block((row - 1, col))
                        self.open_block((row + 1, col))

    def block_is_visible(self, row, col):
        return self.is_visible[row][col]


PAR = Parameters()
BOARD = Board(PAR)
BOARD.init_board()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((PAR.screen_width, PAR.screen_height))
pygame.display.set_caption("Minesweeter")
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.font.Font(pygame.font.get_default_font(), PAR.font_size)


def mouse_to_board_pos(pos):
    x, y = pos[0] - PAR.offset_h, pos[1] - PAR.offset_v
    if not (0 <= x < PAR.columns * PAR.block_size) or not (
        0 <= y < PAR.rows * PAR.block_size
    ):
        return None
    col = x // PAR.block_size
    row = y // PAR.block_size
    return row, col


def draw_transparent_rect(screen, row, col):
    rect = (
        PAR.offset_h + col * PAR.block_size,
        PAR.offset_v + row * PAR.block_size,
        PAR.block_size,
        PAR.block_size,
    )
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, PAR.color_hidden, shape_surf.get_rect())
    screen.blit(shape_surf, rect)


def draw_board():
    height = PAR.rows * PAR.block_size + PAR.line_width // 2
    width = PAR.columns * PAR.block_size + PAR.line_width // 2

    for row in range(PAR.rows):
        for col in range(PAR.columns):
            block = BOARD[row, col]

            # draw numbers
            if 0 < block < 9:
                text = font.render(
                    f"{block}",
                    antialias=True,
                    color=PAR.color_number[block],
                )
                text_rect = text.get_rect()
                # TODO: How does one center this?
                screen.blit(
                    text,
                    dest=(
                        PAR.offset_h
                        + col * PAR.block_size
                        + (PAR.block_size - text_rect.width + PAR.line_width) / 2,
                        PAR.offset_v
                        + row * PAR.block_size
                        + (PAR.block_size - text_rect.height + PAR.line_width) / 2,
                    ),
                )

            # draw bomb
            if block == PAR.id_bomb:
                text = font.render("X", antialias=True, color=(0, 0, 0))
                text_rect = text.get_rect()
                screen.blit(
                    text,
                    dest=(
                        PAR.offset_h
                        + col * PAR.block_size
                        + (PAR.block_size - text_rect.width + PAR.line_width) / 2,
                        PAR.offset_v
                        + row * PAR.block_size
                        + (PAR.block_size - text_rect.height + PAR.line_width) / 2,
                    ),
                )

            # hide invisible blocks
            if not BOARD.block_is_visible(row, col):
                draw_transparent_rect(screen, row, col)

            # draw flags
            if block < 0:
                text = font.render("F", antialias=True, color=PAR.color_flag)
                text_rect = text.get_rect()
                screen.blit(
                    text,
                    dest=(
                        PAR.offset_h
                        + col * PAR.block_size
                        + (PAR.block_size - text_rect.width + PAR.line_width) / 2,
                        PAR.offset_v
                        + row * PAR.block_size
                        + (PAR.block_size - text_rect.height + PAR.line_width) / 2,
                    ),
                )

    # horizontal lines
    for r in range(PAR.rows + 1):
        pygame.draw.line(
            screen,
            PAR.color_line,
            (PAR.offset_h - PAR.line_width // 2, PAR.offset_v + r * PAR.block_size),
            (PAR.offset_h + width, PAR.offset_v + r * PAR.block_size),
            PAR.line_width,
        )

    # vertical lines
    for c in range(PAR.columns + 1):
        pygame.draw.line(
            screen,
            PAR.color_line,
            (PAR.offset_h + c * PAR.block_size, PAR.offset_v - PAR.line_width // 2),
            (PAR.offset_h + c * PAR.block_size, PAR.offset_v + height),
            PAR.line_width,
        )


while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = mouse_to_board_pos(pygame.mouse.get_pos())
            if event.button == 1:  # left click
                BOARD.click_block(pos)
            elif event.button == 3:  # right click
                BOARD.mark_block(pos)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(PAR.color_background)

    draw_board()

    # flip() the display to put on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame
    dt = clock.tick(60) / 1000

pygame.quit()
