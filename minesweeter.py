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

    id_bomb = 9

    # graphics parameters
    block_size = 40
    color_background = (192, 192, 192)
    color_flag = (128, 0, 64)
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
    line_width = 3
    offset_h = 10
    offset_v = 10
    screen_height = 500
    screen_width = 500


PAR = Parameters()


class Board:
    def __init__(self):
        self.board = [[0 for _ in range(PAR.columns)] for _ in range(PAR.rows)]

    def get_block(self, row, col):
        if row < 0 or row >= PAR.rows:
            return 0
        if col < 0 or col >= PAR.columns:
            return 0
        return self.board[row][col]

    def init_board(self):
        # place bombs
        bomb_pos = random.sample(range(PAR.rows * PAR.columns), PAR.bombs)
        for b_p in bomb_pos:
            row = b_p // PAR.columns - 1
            col = b_p % PAR.columns
            self.board[row][col] = PAR.id_bomb

        # place bomb numbers
        for row in range(0, PAR.rows):
            for col in range(0, PAR.columns):
                if self.board[row][col] != 0:
                    continue
                num_bombs = 0
                for i in range(-1, 2):
                    if self.get_block(row + i, col - 1) == PAR.id_bomb:
                        num_bombs += 1
                    if self.get_block(row + i, col + 1) == PAR.id_bomb:
                        num_bombs += 1
                if self.get_block(row - 1, col) == PAR.id_bomb:
                    num_bombs += 1
                if self.get_block(row + 1, col) == PAR.id_bomb:
                    num_bombs += 1
                self.board[row][col] = num_bombs

    def mark_block(self, pos):
        if pos is None:
            return None
        row, col = pos
        self.board[row][col] *= -1

    def open_block(self, pos):
        if pos is None:
            return None
        row, col = pos
        block = self.get_block(row, col)
        if block < 0:
            return None
        if block == PAR.id_bomb:
            print("you lose")


BOARD = Board()
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


def draw_board():
    height = PAR.rows * PAR.block_size
    width = PAR.columns * PAR.block_size

    # horizontal lines
    for r in range(PAR.rows + 1):
        pygame.draw.line(
            screen,
            PAR.color_line,
            (PAR.offset_h, PAR.offset_v + r * PAR.block_size),
            (PAR.offset_h + width, PAR.offset_v + r * PAR.block_size),
            PAR.line_width,
        )
    # vertical lines
    for c in range(PAR.columns + 1):
        pygame.draw.line(
            screen,
            PAR.color_line,
            (PAR.offset_h + c * PAR.block_size, PAR.offset_v),
            (PAR.offset_h + c * PAR.block_size, PAR.offset_v + height),
            PAR.line_width,
        )

    for row in range(PAR.rows):
        for col in range(PAR.columns):
            block = BOARD.get_block(row, col)
            if block == 0:
                continue

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


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = mouse_to_board_pos(pygame.mouse.get_pos())
            if event.button == 1:  # left click
                BOARD.open_block(pos)
            elif event.button == 3:  # right click
                BOARD.mark_block(pos)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(PAR.color_background)

    draw_board()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
