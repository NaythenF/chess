from board import *
from dataclasses import dataclass


@dataclass
class Move:
    x: int
    y: int
    is_capture: bool

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.x == other.x and self.y == other.y
        else:
            return False


class Model:
    def __init__(self):
        self.board = Board()
        self.turn = Color.WHITE
        self.kings = {Color.WHITE: (7, 4), Color.BLACK: (0, 4)}
        self.checks = {}
        self.pins = {}
        self.moves = self.get_moves()
        self.winner = None

    def __getitem__(self, key):
        i, j = key
        return self.board[i, j]

    def switch_turn(self):
        self.turn = self.other_color(self.turn)
        self.moves.clear()
        i, j = self.kings[self.turn]
        self.checks = self.get_checks(i, j)
        self.pins = self.pinned_pieces()
        self.moves = self.get_moves()
        if not self.moves and self.checks:
            self.winner = self.other_color(self.turn)
            print(f"{self.other_color(self.turn)} wins")
        elif not self.moves and not self.checks:
            self.winner = "draw"
            print(f"Draw by stalemate")

    def get_moves(self):
        moves = {}
        print(f"pins:{self.pins}")
        print(f"checks: {self.checks}")
        for i in range(8):
            for j in range(8):
                if self.board[i, j]:
                    piece_type = self.board[i, j].piece_type
                    color = self.board[i, j].color
                    if self.turn == color:
                        piece_moves = self.get_piece_moves(i, j, piece_type)
                        if len(piece_moves) > 0:
                            moves[i, j] = piece_moves
        return moves

    def get_piece_moves(self, i, j, piece_type):
        match piece_type:
            case PieceType.KNIGHT:
                return self.get_knight_moves(i, j)
            case PieceType.BISHOP:
                return self.get_bishop_moves(i, j)
            case PieceType.PAWN:
                return self.get_pawn_moves(i, j)
            case PieceType.QUEEN:
                return self.get_queen_moves(i, j)
            case PieceType.KING:
                return self.get_king_moves(i, j)
            case PieceType.ROOK:
                return self.get_rook_moves(i, j)

    def pawn_capture_dirs(self, color):
        return [(-1, 1), (-1, -1)] if color == Color.WHITE else [(1, -1), (1, 1)]

    def pawn_dirs(self, color):
        return [(-1, 0)] if color == Color.WHITE else [(1, 0)]

    def diagonal_dirs(self):
        return [(-1, -1), (-1, 1), (1, 1), (1, -1)]

    def straight_dirs(self):
        return [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def all_dirs(self):
        return self.straight_dirs() + self.diagonal_dirs()

    def knight_dirs(self):
        return [
            (-2, 1),
            (2, 1),
            (-1, 2),
            (1, 2),
            (2, -1),
            (-2, -1),
            (1, -2),
            (-1, -2),
        ]

    def king_dirs(self):
        return [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ]

    def queen_dirs(self):
        return self.diagonal_dirs() + self.straight_dirs()

    def get_single_moves(self, i_0, j_0, directions):
        moves = []
        for x, y in directions:
            i = i_0 + x
            j = j_0 + y
            if self.valid_position(i, j) and (
                not self.board[i, j]
                or (self.board[i, j] and self.board[i, j].color != self.turn)
            ):
                moves.append(
                    Move(i, j, False) if not self.board[i, j] else Move(i, j, True)
                )
        return moves

    def get_knight_moves(self, i_0, j_0):
        if (i_0, j_0) in self.pins:
            return []

        moves = self.get_single_moves(i_0, j_0, self.knight_dirs())
        if self.checks:
            moves = [
                move for move in moves if (move.x, move.y) in self.possible_squares()
            ]
        return moves

    def get_continuous_moves(self, i_0, j_0, directions):
        moves = []
        for x, y in directions:
            i = i_0 + x
            j = j_0 + y
            while self.valid_position(i, j):
                if not self.board[i, j]:
                    moves.append(Move(i, j, False))
                elif self.board[i, j].color == self.turn:
                    break
                else:
                    moves.append(Move(i, j, True))
                    break
                i += x
                j += y
        return moves

    def get_pawn_moves(self, i_0, j_0):
        has_moved = self.board[i_0, j_0].has_moved
        directions = self.pawn_dirs(self.turn)
        if (i_0, j_0) in self.pins:
            directions = [
                direction
                for direction in directions
                if direction in self.pins[i_0, j_0]
            ]
        if not has_moved:
            directions += [(x * 2, y) for x, y in directions]
        capture_directions = self.pawn_capture_dirs(self.turn)
        moves = []
        for x, y in directions:
            i = i_0 + x
            j = j_0 + y
            if self.valid_position(i, j) and not self.board[i, j]:
                moves.append(Move(i, j, False))
            else:
                break

        for x, y in capture_directions:
            i = i_0 + x
            j = j_0 + y
            if (
                self.valid_position(i, j)
                and self.board[i, j]
                and self.board[i, j].color != self.turn
            ):
                moves.append(Move(i, j, True))

        if self.checks:
            moves = [
                move for move in moves if (move.x, move.y) in self.possible_squares()
            ]
        return moves

    def get_bishop_moves(self, i_0, j_0):
        directions = self.diagonal_dirs()

        if (i_0, j_0) in self.pins:
            directions = [
                direction
                for direction in directions
                if direction in self.pins[i_0, j_0]
            ]
        moves = self.get_continuous_moves(i_0, j_0, directions)
        if self.checks:
            moves = [
                move for move in moves if (move.x, move.y) in self.possible_squares()
            ]
        return moves

    def get_king_moves(self, i_0, j_0):
        moves = self.get_single_moves(i_0, j_0, self.king_dirs())
        return [move for move in moves if self.safe_king_square(move.x, move.y)]

    def get_queen_moves(self, i_0, j_0):
        directions = self.diagonal_dirs() + self.straight_dirs()
        if (i_0, j_0) in self.pins:
            directions = self.pins[i_0, j_0]
        moves = self.get_continuous_moves(i_0, j_0, directions)
        if self.checks:
            moves = [
                move for move in moves if (move.x, move.y) in self.possible_squares()
            ]
        return moves

    def get_rook_moves(self, i_0, j_0):
        directions = self.straight_dirs()
        if (i_0, j_0) in self.pins:
            directions = [
                direction
                for direction in directions
                if direction in self.pins[i_0, j_0]
            ]
        moves = self.get_continuous_moves(i_0, j_0, directions)
        if self.checks:
            moves = [
                move for move in moves if (move.x, move.y) in self.possible_squares()
            ]
        return moves

    def valid_position(self, i, j):
        return i >= 0 and i < 8 and j >= 0 and j < 8

    def other_color(self, color):
        return Color.WHITE if color == Color.BLACK else Color.BLACK

    def get_promotion_x(self, color):
        return 0 if color == Color.WHITE else 7

    def play_move(self, i_0, j_0, move):
        piece = self.board[i_0, j_0]

        for m in self.moves[i_0, j_0]:
            if m == move:
                actual_move = m
                break
        if piece.piece_type == PieceType.KING:
            self.kings[piece.color] = (move.x, move.y)
        piece.has_moved = True
        if piece.piece_type == PieceType.PAWN and move.x == self.get_promotion_x(
            piece.color
        ):
            self.board[move.x, move.y] = Piece(PieceType.QUEEN, piece.color)
        else:
            self.board[move.x, move.y] = piece
        self.board[i_0, j_0] = None
        self.switch_turn()
        return actual_move

    def get_piece_directions(self, piece_type):
        match piece_type:
            case PieceType.QUEEN:
                return self.diagonal_dirs() + self.straight_dirs()
            case PieceType.ROOK:
                return self.straight_dirs()
            case PieceType.BISHOP:
                return self.diagonal_dirs()
            case _:
                return []

    def get_checks(self, i_0, j_0):
        checks = {}
        other = self.other_color(self.turn)
        for x, y in self.all_dirs():
            i = i_0 + x
            j = j_0 + y
            blocks = []
            if (
                (x, y) in self.pawn_capture_dirs(self.turn)
                and self.valid_position(i, j)
                and self.board[i, j]
                and self.board[i, j] == Piece(PieceType.PAWN, other)
            ):
                checks[(i, j)] = []
                continue
            while self.valid_position(i, j):
                piece = self.board[i, j]
                if piece:
                    if (x, y) in self.get_piece_directions(
                        piece.piece_type
                    ) and piece.color == other:
                        checks[(i, j)] = blocks
                    break
                else:
                    blocks.append((i, j))
                i += x
                j += y
        for x, y in self.knight_dirs():
            i = i_0 + x
            j = j_0 + y
            piece = self.board[i, j] if self.valid_position(i, j) else None
            if piece == Piece(PieceType.KNIGHT, other):
                checks[(i, j)] = []
        return checks

    def pinned_pieces(self):
        i_0, j_0 = self.kings[self.turn]
        pins = {}
        for x, y in self.all_dirs():
            i = i_0 + x
            j = j_0 + y
            our_piece = None
            while self.valid_position(i, j):
                piece = self.board[i, j]
                if piece:
                    if piece.color == self.other_color(self.turn):
                        if our_piece and (x, y) in self.get_piece_directions(
                            piece.piece_type
                        ):
                            if our_piece in pins:
                                pins[our_piece].append((x, y))
                            else:
                                pins[our_piece] = [(x, y)]
                        else:
                            break
                    else:
                        if our_piece:
                            break
                        else:
                            our_piece = (i, j)
                i += x
                j += y
        return pins

    def safe_king_square(self, i, j):
        return False if self.get_checks(i, j) else True

    def possible_squares(self):
        if len(self.checks.keys()) > 1:
            return []
        else:
            return list(self.checks.keys()) + [
                block for blocks in self.checks.values() for block in blocks
            ]

    def is_game_over(self):
        return self.winner is not None
