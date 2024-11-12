from position import Position
from constants import BOARD_SIZE
import globals

'''
The class checks for en passant moves, double moves and holds information about 
last row that enables pawn promotion to queen.
'''
class Pawns:
    def __init__(self, is_white):
        self.initial_pawn_positions = []
        self.double_push = None
        self.first_move = [[-1, 0], [-2, 0]]
        self.move = [[-1, 0]]
        self.capture_moves = [[-1, 1], [-1, -1]]

        if is_white:
            self.initial_pawn_positions = [
                Position(6, i) for i in range(BOARD_SIZE)]
            self.promotion_list = [Position(0, i) for i in range(BOARD_SIZE)]
        else:
            self.initial_pawn_positions = [
                Position(1, i) for i in range(BOARD_SIZE)]
            self.promotion_list = [Position(7, i) for i in range(BOARD_SIZE)]

    def is_first_move(self, pos):
        return pos in self.initial_pawn_positions

    def is_en_passant_possible(self, pos, opponent_double_push):
        if opponent_double_push == None:
            return False
        return (pos.y == opponent_double_push.y + 1 or pos.y == opponent_double_push.y - 1) and pos.x == opponent_double_push.x

    def set_double_push(self, pos):
        self.double_push = pos

    def clear_double_push(self):
        self.double_push = None

    def get_double_push(self):
        return self.double_push

    def get_en_passant_move(self, opponent_double_push):
        if globals.IS_WHITES_TURN:
            return Position(opponent_double_push.x - 1, opponent_double_push.y)

        return Position(opponent_double_push.x + 1, opponent_double_push.y)

    def get_possible_capturing_moves(self, pos, board):
        if board[pos.x][pos.y].isupper():
            possible_captures = [Position(pos.x + move[0], pos.y + move[1])
                                 for move in self.capture_moves]
        else:
            possible_captures = [Position(pos.x - move[0], pos.y - move[1])
                                 for move in self.capture_moves]

        valid_captures = []

        for capture in possible_captures:
            if 0 <= capture.x < BOARD_SIZE and 0 <= capture.y < BOARD_SIZE:
                point = board[capture.x][capture.y]

                if point != None:
                    if point.isupper() != board[pos.x][pos.y].isupper():
                        valid_captures.append(capture)

        return valid_captures

    def get_moves(self, pos, board, opponent_double_push):
        capturing_moves = self.get_possible_capturing_moves(pos, board)

        for move in capturing_moves:
            if board[move.x][move.y] == "k" or board[move.x][move.y] == "K":
                return capturing_moves

        if pos in self.initial_pawn_positions:
            if board[pos.x][pos.y].isupper():
                valid_moves = [Position(pos.x + move[0], pos.y + move[1])
                               for move in self.first_move]
            else:
                valid_moves = [Position(pos.x - move[0], pos.y - move[1])
                               for move in self.first_move]

            for i, move in enumerate(valid_moves):
                if board[move.x][move.y] != None:
                    valid_moves.remove(move)

                    if i == 0:
                        valid_moves.clear()

            valid_moves.extend(capturing_moves)
        else:
            if board[pos.x][pos.y].isupper():
                valid_moves = [Position(pos.x + move[0], pos.y + move[1])
                               for move in self.move]
            else:
                valid_moves = [Position(pos.x - move[0], pos.y - move[1])
                               for move in self.move]

            for move in valid_moves:
                if 0 <= move.x < BOARD_SIZE and 0 <= move.y < BOARD_SIZE:
                    if board[move.x][move.y] != None:
                        valid_moves.remove(move)
            valid_moves.extend(capturing_moves)

            if opponent_double_push != None:
                if self.is_en_passant_possible(pos, opponent_double_push):
                    en_passant_move = self.get_en_passant_move(
                        opponent_double_push)
                    valid_moves.append(en_passant_move)

        return valid_moves

    def is_double_move(self, prev_move, curr_move, board):
        if board[curr_move.x][curr_move.y] != None:
            if board[curr_move.x][curr_move.y].isupper():
                if prev_move.x - 2 == curr_move.x and curr_move.y == prev_move.y:
                    return True
            elif prev_move.x + 2 == curr_move.x and curr_move.y == prev_move.y:
                return True

        return False

    def set_double_move(self, pos):
        self.double_push = pos

    def is_promotion(self, pos):
        return pos in self.promotion_list

    def is_en_passant_move(self, pos, opponent_double_push):
        if opponent_double_push == None:
            return False

        if globals.IS_WHITES_TURN:
            return pos.x + 1 == opponent_double_push.x and pos.y == opponent_double_push.y
        else:
            return pos.x - 1 == opponent_double_push.x and pos.y == opponent_double_push.y
