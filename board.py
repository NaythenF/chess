from enum import Enum
from dataclasses import dataclass


class PieceType(Enum):
    KING = 1
    QUEEN = 2
    ROOK = 3
    BISHOP = 4
    KNIGHT = 5
    PAWN = 6


class Color(Enum):
    WHITE = 1
    BLACK = 2


@dataclass
class Piece:
    piece_type: PieceType
    color: Color
    has_moved: bool = False

    def sprite_name(self):
        return f"{self.piece_type.name.lower()}_{self.color.name.lower()}.png"

    def other_color(self):
        return Color.WHITE if self.color == Color.BLACK else Color.BLACK

    def __eq__(self, value):
        if isinstance(value, Piece):
            return self.color == value.color and self.piece_type == value.piece_type
        else:
            return False


class Board:
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]

        # Pawns
        for i in range(8):
            self.squares[1][i] = Piece(PieceType.PAWN, Color.BLACK)
            self.squares[6][i] = Piece(PieceType.PAWN, Color.WHITE)

        # Rooks
        self.squares[0][0] = self.squares[0][7] = Piece(PieceType.ROOK, Color.BLACK)
        self.squares[7][0] = self.squares[7][7] = Piece(PieceType.ROOK, Color.WHITE)

        # Knights
        self.squares[0][1] = self.squares[0][6] = Piece(PieceType.KNIGHT, Color.BLACK)
        self.squares[7][1] = self.squares[7][6] = Piece(PieceType.KNIGHT, Color.WHITE)

        # Bishops
        self.squares[0][2] = self.squares[0][5] = Piece(PieceType.BISHOP, Color.BLACK)
        self.squares[7][2] = self.squares[7][5] = Piece(PieceType.BISHOP, Color.WHITE)

        # Kings
        self.squares[0][4] = Piece(PieceType.KING, Color.BLACK)
        self.squares[7][4] = Piece(PieceType.KING, Color.WHITE)

        # Queens
        self.squares[0][3] = Piece(PieceType.QUEEN, Color.BLACK)
        self.squares[7][3] = Piece(PieceType.QUEEN, Color.WHITE)

    def __getitem__(self, key):
        i, j = key
        return self.squares[i][j]

    def __setitem__(self, key, item):
        i, j = key
        self.squares[i][j] = item
