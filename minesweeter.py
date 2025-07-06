import random
import math
import pygame

p = dict()
p["bombs"] = 10
p["columns"] = 9
p["line-width"] = 3
p["offset-h"] = 10
p["offset-v"] = 10
p["rows"] = 9
p["screen-height"] = 500
p["screen-width"] = 500
p["square-size"] = 40

p["font-size"] = math.ceil(0.8 * p["square-size"])

number_colors = [
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
background_color = (192, 192, 192)
line_color = (128, 128, 128)


def get_block(board, row, col):
    if row < 0 or row >= p["rows"]:
        return 0
    if col < 0 or col >= p["columns"]:
        return 0
    return board[row][col]


def init_board():
    board = [[0 for _ in range(p["columns"])] for _ in range(p["rows"])]

    bombs = random.sample(range(p["rows"] * p["columns"]), p["bombs"])
    for bomb in bombs:
        row = bomb // p["columns"] - 1
        col = bomb % p["columns"]
        board[row][col] = -1

    for row in range(0, p["rows"]):
        for col in range(0, p["columns"]):
            if board[row][col] != 0:
                continue
            num_bombs = 0
            for i in range(-1, 2):
                if get_block(board, row + i, col - 1) == -1:
                    num_bombs += 1
                if get_block(board, row + i, col + 1) == -1:
                    num_bombs += 1
            if get_block(board, row - 1, col) == -1:
                num_bombs += 1
            if get_block(board, row + 1, col) == -1:
                num_bombs += 1
            board[row][col] = num_bombs

    return board


board = init_board()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((p["screen-width"], p["screen-height"]))
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.font.Font(pygame.font.get_default_font(), p["font-size"])


def mouse_to_board_pos(pos):
    x, y = pos[0] - p["offset-h"], pos[1] - p["offset-v"]
    if not (0 <= x < p["columns"] * p["square-size"]) or not (
        0 <= y < p["rows"] * p["square-size"]
    ):
        return None
    col = x // p["square-size"]
    row = y // p["square-size"]
    return row, col


def mark_block(pos):
    if pos is None:
        return None
    row, col = pos
    board[row][col] = -2


def open_block(pos):
    if pos is None:
        return None
    row, col = pos
    board[row][col] = 2


def draw_board():
    height = p["rows"] * p["square-size"]
    width = p["columns"] * p["square-size"]

    # horizontal lines
    for r in range(p["rows"] + 1):
        pygame.draw.line(
            screen,
            line_color,
            (p["offset-h"], p["offset-v"] + r * p["square-size"]),
            (p["offset-h"] + width, p["offset-v"] + r * p["square-size"]),
            p["line-width"],
        )
    # vertical lines
    for c in range(p["columns"] + 1):
        pygame.draw.line(
            screen,
            line_color,
            (p["offset-h"] + c * p["square-size"], p["offset-v"]),
            (p["offset-h"] + c * p["square-size"], p["offset-v"] + height),
            p["line-width"],
        )

    for row in range(p["rows"]):
        for col in range(p["columns"]):
            block = board[row][col]
            if block == 0:
                continue

            if 0 < block < 9:
                text = font.render(
                    f"{board[row][col]}", antialias=True, color=number_colors[block]
                )
                text_rect = text.get_rect()
                # TODO: How does one center this?
                screen.blit(
                    text,
                    dest=(
                        p["offset-h"]
                        + col * p["square-size"]
                        + (p["square-size"] - text_rect.width + p["line-width"]) / 2,
                        p["offset-v"]
                        + row * p["square-size"]
                        + (p["square-size"] - text_rect.height + p["line-width"]) / 2,
                    ),
                )

            if block == -1:
                text = font.render("X", antialias=True, color=(0, 0, 0))
                text_rect = text.get_rect()
                screen.blit(
                    text,
                    dest=(
                        p["offset-h"]
                        + col * p["square-size"]
                        + (p["square-size"] - text_rect.width + p["line-width"]) / 2,
                        p["offset-v"]
                        + row * p["square-size"]
                        + (p["square-size"] - text_rect.height + p["line-width"]) / 2,
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
                open_block(pos)
            elif event.button == 3:  # right click
                mark_block(pos)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)

    draw_board()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
