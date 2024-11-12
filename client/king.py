from position import Position
from constants import *
import globals

'''
The class contains information about castling and king valid moves.
'''
class King:
    def __init__(self, piece):
        self.check = False
        self.valid_moves = []
        self.position = None
        self.piece = piece
        self.is_white = piece.isupper()
        self.has_moved = False
        self.has_left_rook_moved = False
        self.has_right_rook_moved = False
        self.has_already_castled = False
        self.is_long_castle_collision = False
        self.is_short_castle_collision = False
        self.is_long_castle_possible = True
        self.is_short_castle_possible = True

        if self.is_white:
            self.long_castle_empty_squares = [Position(BOARD_SIZE - 1, 1),
                                              Position(BOARD_SIZE - 1, 2),
                                              Position(BOARD_SIZE - 1, 3)]
            self.short_castle_empty_squares = [Position(BOARD_SIZE - 1, 5),
                                               Position(BOARD_SIZE - 1, 6)]
            self.perform_short_castle_pos = Position(BOARD_SIZE - 1, 6)
            self.perform_long_castle_pos = Position(BOARD_SIZE - 1, 2)
            self.left_rook_pos = Position(BOARD_SIZE - 1, 0)
            self.right_rook_pos = Position(BOARD_SIZE - 1, BOARD_SIZE - 1)
        else:
            self.long_castle_empty_squares = [Position(0, 1),
                                              Position(0, 2),
                                              Position(0, 3)]
            self.short_castle_empty_squares = [Position(0, 5), Position(0, 6)]
            self.perform_short_castle_pos = Position(0, 6)
            self.perform_long_castle_pos = Position(0, 2)
            self.left_rook_pos = Position(0, 0)
            self.right_rook_pos = Position(0, BOARD_SIZE - 1)

    def can_long_castle(self, board):
        if self.has_moved or self.is_long_castle_collision or not self.is_long_castle_possible:
            return False

        if self.is_white:
            rook = "R"
            row = board[BOARD_SIZE - 1]
        else:
            rook = "r"
            row = board[0]

        if row[1] == None and row[2] == None and row[3] == None and row[0] == rook and not self.has_left_rook_moved:
            return True

        return False

    def can_short_castle(self, board):
        if self.has_moved or self.is_short_castle_collision or not self.is_short_castle_possible:
            return False

        if self.is_white:
            rook = "R"
            row = board[BOARD_SIZE - 1]
        else:
            rook = "r"
            row = board[0]

        if row[5] == None and row[6] == None and row[7] == rook and not self.has_right_rook_moved:
            return True

        return False

    def set_rook_has_moved(self, pos):
        if globals.IS_WHITES_TURN:
            if pos == self.left_rook_pos:
                self.has_left_rook_moved = True
                self.is_long_castle_possible = False
        else:
            if pos == self.right_rook_pos:
                self.has_right_rook_moved = True
                self.is_right_castle_possible = False

    def set_has_moved(self):
        self.has_moved = True
        self.is_long_castle_possible = False
        self.is_short_castle_possible = False

    def get_short_castle_pos(self):
        return self.perform_short_castle_pos

    def get_long_castle_pos(self):
        return self.perform_long_castle_pos

    def set_is_long_castle_collision(self, is_collision):
        self.is_long_castle_collision = is_collision

    def set_is_short_castle_collision(self, is_collision):
        self.is_short_castle_collision = is_collision

    def get_long_castle_empty_squares(self):
        return self.long_castle_empty_squares

    def get_short_castle_empty_squares(self):
        return self.short_castle_empty_squares

    def get_pos_after_short_castle(self):
        return self.perform_short_castle_pos

    def get_pos_after_long_castle(self):
        return self.perform_long_castle_pos

    def set_is_long_castle_possible(self, is_possible):
        self.is_long_castle_possible = is_possible

    def set_is_short_castle_possible(self, is_possible):
        self.is_short_castle_possible = is_possible

    def get_is_short_castle_possible(self):
        return self.is_short_castle_possible

    def get_is_long_castle_possible(self):
        return self.is_long_castle_possible

    def set_pos(self, pos):
        self.position = pos
