import pygame
from board import Board, Piece, PieceType, Color
from model import Model, Move
import os
import math

directory = os.path.dirname(os.path.realpath(__file__))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
model = Model()
piece_selected = None
running = True

# random vars
white = pygame.color.THECOLORS["white"]
gray = pygame.color.THECOLORS["gray"]
black = pygame.color.THECOLORS["black"]
red = pygame.color.THECOLORS["red"]

grid_size = 720 / 8
sprites = {
    (piece, color): pygame.transform.scale(
        pygame.image.load(
            f"{directory}\\assets\\{color.name.lower()}_{piece.name.lower()}.png"
        ),
        (grid_size, grid_size),
    )
    for color in Color
    for piece in PieceType
}


def other_color(color):
    if color == Color.BLACK:
        return Color.WHITE
    else:
        return Color.BLACK


sounds = {
    "move": pygame.mixer.Sound(f"{directory}\\assets\\move.mp3"),
    "capture": pygame.mixer.Sound(f"{directory}\\assets\\capture.mp3"),
    "check": pygame.mixer.Sound(f"{directory}\\assets\\check.mp3"),
    "end": pygame.mixer.Sound(f"{directory}\\assets\\end.mp3"),
}
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    my, mx = pygame.mouse.get_pos()
    mx = math.floor(mx / grid_size)
    my = math.floor(my / grid_size)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            y, x = event.pos
            x = math.floor(x / grid_size)
            y = math.floor(y / grid_size)
            if event.button == 3:
                if piece_selected:
                    piece_selected = None
            elif event.button == 1:
                if (
                    piece_selected
                    and piece_selected in model.moves
                    and Move(x, y, True) in model.moves[piece_selected]
                ):
                    move_played = model.play_move(
                        piece_selected[0], piece_selected[1], Move(x, y, False)
                    )
                    if model.is_game_over():
                        pygame.mixer.Sound.play(sounds["end"])
                        pygame.mixer.music.stop()
                    elif model.checks:
                        pygame.mixer.Sound.play(sounds["check"])
                        pygame.mixer.music.stop()
                    elif move_played.is_capture:
                        pygame.mixer.Sound.play(sounds["capture"])
                        pygame.mixer.music.stop()
                    else:
                        pygame.mixer.Sound.play(sounds["move"])
                        pygame.mixer.music.stop()

                    piece_selected = None
                else:
                    if model[x, y] and model[x, y].color == model.turn:
                        piece_selected = (x, y)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")
    for i in range(8):
        for j in range(8):
            rect = pygame.Rect(
                j * grid_size,
                i * grid_size,
                grid_size,
                grid_size,
            )
            pygame.draw.rect(
                width=int(grid_size),
                rect=rect,
                surface=screen,
                color=white if (i % 2) == (j % 2) else gray,
            )
            piece = model[i, j]
            if piece:
                screen.blit(sprites[(piece.piece_type, piece.color)], rect)

    if (mx, my) in model.moves.keys():
        for move in model.moves[mx, my]:
            rect = pygame.Rect(
                move.y * grid_size,
                move.x * grid_size,
                grid_size,
                grid_size,
            )
            if (
                not piece_selected
                and model[mx, my]
                and model[mx, my].color == model.turn
            ):
                pygame.draw.circle(
                    screen,
                    red if move.is_capture else black,
                    (
                        move.y * grid_size + grid_size / 2,
                        move.x * grid_size + grid_size / 2,
                    ),
                    10,
                )

    if piece_selected:
        x, y = piece_selected
        if (x, y) in model.moves.keys():
            for move in model.moves[x, y]:
                rect = pygame.Rect(
                    move.y * grid_size,
                    move.x * grid_size,
                    grid_size,
                    grid_size,
                )
                pygame.draw.circle(
                    screen,
                    red if move.is_capture else black,
                    (
                        move.y * grid_size + grid_size / 2,
                        move.x * grid_size + grid_size / 2,
                    ),
                    10,
                )

        pygame.draw.circle(
            screen,
            black,
            (
                y * grid_size + grid_size / 2,
                x * grid_size + grid_size / 2,
            ),
            grid_size / 2,
            2,
        )
    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
