import argparse
from dataclasses import dataclass
from math import ceil, floor
import pygame
import random

parser = argparse.ArgumentParser()
parser.add_argument("-s", type=int, help="random seed", default=0)
args = parser.parse_args()


seed = args.s
if seed == 0:
    seed = random.randint(10_000_000, 100_000_000)
print(seed)
random.seed(seed)


@dataclass
class Parameters:
    # game parameters
    num_mines = 10
    columns = 9
    rows = 9

    id_air = 9
    id_losing_mine = 11
    id_mine = 10

    # graphics parameters
    block_size = 100
    font_size = ceil(0.8 * block_size)
    font_size_counters = ceil(1.5 * block_size)
    line_width = 15
    offset_h = block_size // 2
    offset_v = 2.5 * block_size
    screen_height = block_size * 12
    screen_width = block_size * 10
    start_button_size = 1.5 * block_size
    start_button_tl_coords = ((screen_width - start_button_size) // 2, block_size // 2)

    # colors
    color_state_loss = (255, 0, 0)
    color_state_neutral = (255, 255, 0)
    color_state_win = (0, 255, 0)
    color_background = (192, 192, 192)
    color_counters = (255, 0, 0)
    color_flag = (128, 0, 64)
    color_hidden = (100, 100, 100, 200)
    color_line = (128, 128, 128)
    color_losing_mine = (255, 0, 0)
    color_mine = (0, 0, 0)
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


class Board:
    def __init__(self, par):
        self.par = par

        self.board = list()
        self.first_left_click = True
        self.flag_counter = 0
        self.is_visible = list()
        self.mine_positions = list()
        self.state = 0

    def init(self):
        self.board = [self.par.id_air] * self.par.columns * self.par.rows
        self.first_left_click = True
        self.flag_counter = self.par.num_mines
        self.is_visible = [False] * self.par.columns * self.par.rows
        self.mine_positions = random.sample(
            range(self.par.rows * self.par.columns), self.par.num_mines
        )
        self.state = 0

    def to_linear(self, key):
        if type(key) is int:
            if 0 <= key and key < len(self.board):
                return key
        elif type(key) is tuple and len(key) == 2:
            if 0 <= key[0] and key[0] < self.par.rows:
                if 0 <= key[1] and key[1] < self.par.columns:
                    return key[0] * self.par.columns + key[1]

    def linear_to_grid(self, key):
        row = key // self.par.columns
        col = key % self.par.columns
        return row, col

    def __getitem__(self, key):
        _key = self.to_linear(key)
        if _key is not None:
            return self.board[_key]

    def __setitem__(self, key, val):
        _key = self.to_linear(key)
        if _key is not None:
            self.board[_key] = val

    def _neighbors(self, key):
        _key = self.to_linear(key)
        if key is not None:
            row, col = self.linear_to_grid(_key)
            neighbors = list()
            for i in range(-1, 2):
                neighbors.append((row + i, col - 1))
                neighbors.append((row + i, col + 1))
            neighbors.append((row - 1, col))
            neighbors.append((row + 1, col))
        _neighbors = [self.to_linear(neighbor) for neighbor in neighbors]
        return [neighbor for neighbor in _neighbors if neighbor is not None]

    def init_board(self):
        self.init()

        # place mines
        for m_p in self.mine_positions:
            self.__setitem__(m_p, self.par.id_mine)

        # place mine numbers
        for key in range(len(self.board)):
            if self.board[key] != self.par.id_air:
                continue
            mine_counter = 0
            for n_key in self._neighbors(key):
                if self.board[n_key] == self.par.id_mine:
                    mine_counter += 1
            if mine_counter > 0:
                self.board[key] = mine_counter

    def flag(self, pos):
        if self.state != 0:
            return None

        _key = self.to_linear(pos)
        if _key is None:
            return None

        if self.is_visible[_key]:
            return None

        if self.board[_key] > 0:
            self.flag_counter -= 1
        else:
            self.flag_counter += 1
        self.board[_key] *= -1

        return self.state

    def unveil(self, pos):
        _key = self.to_linear(pos)
        if _key is None:
            return None

        if self.is_visible[_key]:
            return None

        block = self.board[_key]

        if block == self.par.id_mine:
            self.board[_key] = self.par.id_losing_mine
            for m_p in self.mine_positions:
                self.is_visible[m_p] = True
            self.state = -1
        else:
            if block > 0:
                self.is_visible[_key] = True

            if block == self.par.id_air:
                # unveil connecting air and number blocks
                for n_key in self._neighbors(_key):
                    if self.board[n_key] == self.par.id_air or (
                        0 < self.board[n_key] and self.board[n_key] < 9
                    ):
                        self.unveil(n_key)

    def click(self, pos):
        if self.state != 0:
            return None

        _key = self.to_linear(pos)
        if _key is None:
            return None

        block = self.board[_key]

        if self.first_left_click:
            self.first_left_click = False
            if self.board[_key] == self.par.id_mine:
                self.init_board()
                self.click(pos)
                return None

        if block < 0:  # block is flagged
            return None
        else:
            self.unveil(pos)

            if self.is_visible[_key]:
                if 0 < block < 9:
                    # count flags surrounding the block
                    num_flags = 0
                    for n_key in self._neighbors(_key):
                        if self.board[n_key] < 0:
                            num_flags += 1

                    # unveil all surrounding blocks
                    if num_flags == block:
                        for n_key in self._neighbors(_key):
                            self.unveil(n_key)

        # check win condition
        if len(self.board) - sum(self.is_visible) == self.par.num_mines:
            for m_p in self.mine_positions:
                self.board[m_p] = -self.par.id_mine
            self.state = 1

        return self.state

    def block_is_visible(self, row, col):
        _key = self.to_linear((row, col))
        if _key is None:
            return False
        else:
            return self.is_visible[_key]


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
font_counters = pygame.font.SysFont("liberationmono", PAR.font_size_counters)


def clicked_new_game(pos):
    if (
        PAR.start_button_tl_coords[0] <= pos[0]
        and pos[0] <= PAR.start_button_tl_coords[0] + PAR.start_button_size
    ):
        if (
            PAR.start_button_tl_coords[1] <= pos[1]
            and pos[1] <= PAR.start_button_tl_coords[1] + PAR.start_button_size
        ):
            return True
    return False


def mouse_to_board_pos(pos):
    x, y = pos[0] - PAR.offset_h, pos[1] - PAR.offset_v
    if not (0 <= x < PAR.columns * PAR.block_size) or not (
        0 <= y < PAR.rows * PAR.block_size
    ):
        return None
    col = round(x // PAR.block_size)
    row = round(y // PAR.block_size)
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


def draw(seconds):
    height = PAR.rows * PAR.block_size + PAR.line_width // 2
    width = PAR.columns * PAR.block_size + PAR.line_width // 2

    # flag counter
    if BOARD.flag_counter >= 0:
        s = f"{BOARD.flag_counter:03}"
    else:
        s = f"{BOARD.flag_counter}"
        if len(s) == 2:
            s = "0" + s
    text = font_counters.render(s, antialias=True, color=PAR.color_counters)
    text_rect = text.get_rect()
    screen.blit(
        text,
        dest=(PAR.offset_h, PAR.block_size // 2),
    )

    # seconds counter
    text = font_counters.render(
        f"{floor(seconds):03}", antialias=True, color=PAR.color_counters
    )
    text_rect = text.get_rect()
    screen.blit(
        text,
        dest=(
            PAR.screen_width - PAR.offset_h - 3 * PAR.block_size,
            PAR.block_size // 2,
        ),
    )

    # start/stop button
    pygame.draw.rect(
        screen,
        PAR.color_hidden,
        (*PAR.start_button_tl_coords, PAR.start_button_size, PAR.start_button_size),
    )
    state_color = PAR.color_state_neutral
    if BOARD.state == 1:
        state_color = PAR.color_state_win
    elif BOARD.state == -1:
        state_color = PAR.color_state_loss
    pygame.draw.circle(
        screen,
        state_color,
        (PAR.screen_width // 2, (0.5 + 1.5 / 2) * PAR.block_size),
        PAR.block_size // 2,
        PAR.block_size // 2,
    )

    # board
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

            # draw (losing) mine
            if block == PAR.id_mine or block == PAR.id_losing_mine:
                if block == PAR.id_mine:
                    text = font.render("X", antialias=True, color=PAR.color_mine)
                else:
                    text = font.render("X", antialias=True, color=PAR.color_losing_mine)
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


dt_accu = 0
game_running = False
while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if clicked_new_game(pos):
                game_running = False
                dt_accu = 0
                BOARD.init_board()
            else:
                pos = mouse_to_board_pos(pos)
                if event.button == 1:  # left click
                    state = BOARD.click(pos)
                    if state == 0:
                        game_running = True
                    else:
                        game_running = False
                elif event.button == 3:  # right click
                    state = BOARD.flag(pos)
                    if state == 0:
                        game_running = True
                    else:
                        game_running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(PAR.color_background)

    draw(dt_accu)

    # flip() the display to put on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame
    dt = clock.tick(60) / 1000
    if game_running:
        dt_accu += dt

pygame.quit()

# row = b_p // self.par.columns
# col = b_p % self.par.columns
