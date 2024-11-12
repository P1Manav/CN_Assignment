import copy
from king import King
from constants import *
from collections import defaultdict
from position import Position
from pawns import Pawns
import globals


class Game:
    # all of the possible moves are calculated by adding the vectors to the coordinates of clicked position
    def __init__(self):
        self.possible_moves = defaultdict(list, {
            "R": [[-1, 0], [1, 0], [0, 1], [0, -1]],
            "B": [[-1, -1], [-1, 1], [1, 1], [1, -1]],
            "Q": [[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, 0], [1, 0], [0, 1], [0, -1]],
            "N": [[-2, 1], [-1, 2], [1, 2], [2, 1], [-1, -2], [-2, -1], [1, -2], [2, -1]],
            "K": [[-1, 0], [1, 0], [0, 1], [0, -1], [-1, -1], [-1, 1], [1, 1], [1, -1]],
        })

        self.board = []

        self.white_king = King("K")
        self.black_king = King("k")

        self.white_pawns = Pawns(is_white=True)
        self.black_pawns = Pawns(is_white=False)
        self.all_moves = []

    # when the user changes his position all of the valid moves are calculated and the collision with king is being checked
    # when the position of a given piece collides with the king, the valid move of a king gets deleted.
    # for every move of a king the possibility of short castle and long castle is being checked
    # when a move causes players own king to be in check, the move gets deleted and the piece is pinned (has no valid moves)
    def get_valid_moves(self, square):
        square_x = square.x
        square_y = square.y
        piece = self.board[square_x][square_y]
        is_white = self.board[square_x][square_y].isupper()
        valid_moves = []

        if self.is_queen_rook_bishop(piece):
            valid_moves = self.get_rook_queen_bishop_valid_moves(
                piece, square, self.board)
            valid_moves = self.get_legal_moves(
                valid_moves, piece, square)
        else:
            if piece == "n" or piece == "N":
                valid_moves = self.get_knight_valid_moves(
                    piece, square)
                valid_moves = self.get_legal_moves(
                    valid_moves, piece, square)
            elif self.is_pawn(piece):
                valid_moves = self.get_pawn_valid_moves(square)
                valid_moves = self.get_legal_moves(
                    valid_moves, piece, square)
            elif piece == "k" or piece == "K":
                if not is_white:
                    self.black_king.position = square
                    valid_moves = self.black_king.valid_moves

                    if not self.black_king.check:
                        if self.black_king.can_short_castle(self.board):
                            valid_moves.append(
                                self.black_king.get_short_castle_pos())

                        if self.black_king.can_long_castle(self.board):
                            valid_moves.append(
                                self.black_king.get_long_castle_pos())

                else:
                    self.white_king.position = square

                    valid_moves = self.white_king.valid_moves

                    if not self.white_king.check:
                        if self.white_king.can_short_castle(self.board):
                            valid_moves.append(
                                self.white_king.get_short_castle_pos())

                        if self.white_king.can_long_castle(self.board):
                            valid_moves.append(
                                self.white_king.get_long_castle_pos())

        self.check_collision_with_king_moves(is_white)

        if self.is_pawn(piece):
            if piece.isupper():
                capturing_moves = self.white_pawns.get_possible_capturing_moves(
                    square, self.board)
            else:
                capturing_moves = self.black_pawns.get_possible_capturing_moves(
                    square, self.board)

            self.check_castling_collision(is_white, capturing_moves)
        else:
            self.check_castling_collision(is_white, valid_moves)

        if self.is_opponent_being_checked(valid_moves, piece):
            if is_white:
                self.black_king.check = True
            else:
                self.white_king.check = True

        return valid_moves

    def check_collision_with_king_moves(self, is_white):
        if is_white:
            king = self.black_king
        else:
            king = self.white_king

        for move in king.valid_moves:
            board_copy = copy.deepcopy(self.board)
            x = move.x
            y = move.y

            king_copy = copy.deepcopy(king)
            king_copy.position = move
            board_copy[x][y] = king.piece
            prev_pos = king.position
            board_copy[prev_pos.x][prev_pos.y] = None

            if self.is_own_king_in_check(board_copy, king_copy):
                king.valid_moves.remove(move)

    def get_initial_king_moves(self, pos):
        square_x = pos.x
        square_y = pos.y
        valid_moves = []
        piece = self.board[square_x][square_y]
        is_white = piece.isupper()

        squares = [Position(square_x + direction[0], square_y + direction[1])
                   for direction in self.possible_moves["K"]]
        for square in squares:
            x = square.x
            y = square.y

            if 0 <= square.x < BOARD_SIZE and 0 <= square.y < BOARD_SIZE:
                if self.board[x][y] == None:
                    valid_moves.append(square)
                elif self.board[x][y].isupper() != is_white:
                    valid_moves.append(square)
        return valid_moves

    def get_king_valid_moves(self, square):
        square_x = square.x
        square_y = square.y
        piece = self.board[square_x][square_y]

        is_white = piece.isupper()

        if not is_white:
            return self.black_king.valid_moves
        else:
            return self.white_king.valid_moves

    def clear_king_moves(self):
        self.white_king.valid_moves.clear()
        self.black_king.valid_moves.clear()
        self.white_king.check = False
        self.black_king.check = False

        self.black_king.set_is_short_castle_collision(False)
        self.black_king.set_is_long_castle_collision(False)

        self.white_king.set_is_short_castle_collision(False)
        self.white_king.set_is_long_castle_collision(False)

    def get_white_king(self):
        return self.white_king

    def get_black_king(self):
        return self.black_king

    def set_white_king_moves(self, moves):
        self.white_king.valid_moves = moves

    def set_black_king_moves(self, moves):
        self.black_king.valid_moves = moves

    def is_own_king_in_check(self, board, king):
        valid_moves = []

        for x, row in enumerate(board):
            for y, piece in enumerate(row):
                if piece != None and piece != "k" and piece != "K":
                    pos = Position(x, y)

                    if self.is_queen_rook_bishop(piece):
                        valid_moves = self.get_rook_queen_bishop_valid_moves(
                            piece, pos, board)
                    elif piece == "n" or piece == "N":
                        valid_moves = self.get_knight_valid_moves(
                            piece, pos)
                    elif self.is_pawn(piece):
                        if piece.isupper():
                            valid_moves = self.white_pawns.get_possible_capturing_moves(
                                pos, board)
                        else:
                            valid_moves = self.black_pawns.get_possible_capturing_moves(
                                pos, board)

                    if king.position in valid_moves and king.piece.isupper() != piece.isupper():
                        return True

        return False

    # to calculate queen, bishop or rook valid moves, we add a given vector to a clicked position
    # until the position reaches the end of a board or it collides with some piece
    def get_rook_queen_bishop_valid_moves(self, piece, pos, board):
        valid_moves = []
        squares = [Position(pos.x + direction[0], pos.y + direction[1])
                   for direction in self.possible_moves[piece.upper()]]

        for i, square in enumerate(squares):
            square_copy = copy.deepcopy(square)

            while True:
                x = square_copy.x
                y = square_copy.y
                piece_directions = self.possible_moves[piece.upper()]

                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                    if board[x][y] == None:
                        valid_moves.append(square_copy)
                        square_copy = Position(piece_directions[i][0] + x,
                                               piece_directions[i][1] + y)
                    else:
                        valid_moves.append(square_copy)
                        square_copy = Position(piece_directions[i][0] + x,
                                               piece_directions[i][1] + y)
                        break
                else:
                    break
        return valid_moves

    # knight valid moves are being calculated by adding the vector to a clicked position
    def get_knight_valid_moves(self, piece, pos):
        valid_moves = []
        squares = [Position(pos.x + direction[0], pos.y + direction[1])
                   for direction in self.possible_moves[piece.upper()]]
        for square in squares:
            x = square.x
            y = square.y

            if 0 <= square.x < BOARD_SIZE and 0 <= square.y < BOARD_SIZE:
                if self.board[x][y] == None:
                    valid_moves.append(square)
                else:
                    valid_moves.append(square)

        return valid_moves

    # legal moves are moves that don't lead to a players own king getting checked (the pin)
    def get_legal_moves(self, valid_moves, piece, prev_pos):
        valid_moves_copy = copy.deepcopy(valid_moves)

        for move in valid_moves_copy:
            board_copy = copy.deepcopy(self.board)
            x = move.x
            y = move.y
            board_copy[x][y] = piece

            prev_x = prev_pos.x
            prev_y = prev_pos.y

            board_copy[prev_x][prev_y] = None

            if piece.isupper():
                if self.is_own_king_in_check(board_copy, self.white_king):
                    valid_moves.remove(move)
            else:
                if self.is_own_king_in_check(board_copy, self.black_king):
                    valid_moves.remove(move)

        return valid_moves

    def is_opponent_being_checked(self, valid_moves, piece):
        is_piece_white = piece.isupper()

        if not is_piece_white:
            if self.white_king.position in valid_moves:
                return True
        elif self.black_king.position in valid_moves:
            return True

        return False

    def is_checkmate(self):
        if self.white_king.check and self.white_king.valid_moves == []:
            return not self.are_valid_moves_left(white=True)

        if self.black_king.check and self.black_king.valid_moves == []:
            return not self.are_valid_moves_left(white=False)

        return False

    def are_valid_moves_left(self, white):
        for x, row in enumerate(self.board):
            for y, piece in enumerate(row):
                valid_moves = []
                pos = Position(x, y)

                if piece != None:
                    if piece.isupper() == white:
                        if self.is_queen_rook_bishop(piece):
                            valid_moves = self.get_rook_queen_bishop_valid_moves(
                                piece, pos, self.board)
                            valid_moves = self.get_legal_moves(
                                valid_moves, piece, pos)
                        else:
                            if piece == "n" or piece == "N":
                                valid_moves = self.get_knight_valid_moves(
                                    piece, pos)
                                valid_moves = self.get_legal_moves(
                                    valid_moves, piece, pos)
                            elif self.is_pawn(piece):
                                valid_moves = self.get_pawn_valid_moves(pos)
                                valid_moves = self.get_legal_moves(
                                    valid_moves, piece, pos)

                        if self.is_king(piece):
                            if white:
                                valid_moves = self.white_king.valid_moves
                            else:
                                valid_moves = self.black_king.valid_moves

                        for move in copy.deepcopy(valid_moves):
                            if self.board[move.x][move.y] != None:
                                if self.board[move.x][move.y].isupper() == white:
                                    valid_moves.remove(move)

                        if len(valid_moves) != 0:
                            return True
        return False

    def get_board(self):
        return self.board

    def update(self, pos, piece):
        self.board[pos.x][pos.y] = piece

    def is_queen_rook_bishop(self, piece):
        if piece == "R" or piece == "r" \
                or piece == "B" or piece == "b" \
                or piece == "Q" or piece == "q":
            return True

        return False

    # checks pawn moves that can include a double push or capturing possibility
    def get_pawn_valid_moves(self, pos):
        valid_moves = []

        if self.board[pos.x][pos.y] != None:
            if self.board[pos.x][pos.y].isupper():
                opponent_double_push = self.black_pawns.get_double_push()
                valid_moves = self.white_pawns.get_moves(
                    pos, self.board, opponent_double_push)
            else:
                opponent_double_push = self.white_pawns.get_double_push()
                valid_moves = self.black_pawns.get_moves(
                    pos, self.board, opponent_double_push)

        return valid_moves

    def clear_opponent_double_push(self):
        if globals.IS_WHITES_TURN:
            self.black_pawns.clear_double_push()
        else:
            self.white_pawns.clear_double_push()

    def is_pawn_double_move(self, prev_move, curr_move):
        if globals.IS_WHITES_TURN:
            return self.white_pawns.is_double_move(prev_move, curr_move, self.board)
        else:
            return self.black_pawns.is_double_move(prev_move, curr_move, self.board)

    def set_pawn_double_push(self, pos):
        if globals.IS_WHITES_TURN:
            self.white_pawns.set_double_move(pos)
        else:
            self.black_pawns.set_double_move(pos)

    def is_promotion(self, pos):
        if globals.IS_WHITES_TURN:
            return self.white_pawns.is_promotion(pos)
        else:
            return self.black_pawns.is_promotion(pos)

    def is_en_passant_move(self, pos, opponent_double_push):
        if globals.IS_WHITES_TURN:
            return self.white_pawns.is_en_passant_move(pos, opponent_double_push)
        else:
            return self.black_pawns.is_en_passant_move(pos, opponent_double_push)

    def get_opponent_pawn_position(self):
        if globals.IS_WHITES_TURN:
            return self.black_pawns.get_double_push()
        else:
            return self.white_pawns.get_double_push()

    def is_pawn(self, piece):
        return piece == "p" or piece == "P"

    def is_black_in_check(self):
        return self.black_king.check

    def is_white_in_check(self):
        return self.white_king.check

    def is_stalemate(self):
        stalemate = not self.are_valid_moves_left(white=True) and \
            not self.white_king.check

        if stalemate:
            return stalemate

        if not stalemate:
            return not self.are_valid_moves_left(white=False) and not self.black_king.check

    def set_black_king_has_moved(self):
        self.black_king.set_has_moved()

    def set_white_king_has_moved(self):
        self.white_king.set_has_moved()

    def set_rook_has_moved(self, pos):
        if globals.IS_WHITES_TURN:
            self.white_king.set_rook_has_moved(pos)
        else:
            self.black_king.set_rook_has_moved(pos)

    def is_rook(self, piece):
        return piece == "r" or piece == "R"

    # when castling would lead to a king getting checked, the move is removed from the valid king moves
    def check_castling_collision(self, is_piece_white, valid_moves):
        if not is_piece_white:
            opposite_king = self.white_king
        else:
            opposite_king = self.black_king

        pos_after_long_castle = opposite_king.get_pos_after_long_castle()
        pos_after_short_castle = opposite_king.get_pos_after_short_castle()

        for move in valid_moves:
            if move == pos_after_long_castle or opposite_king.check:
                opposite_king.set_is_long_castle_collision(False)

                if move in opposite_king.valid_moves:
                    opposite_king.valid_moves.remove(move)
                break

            if move == pos_after_short_castle or opposite_king.check:
                opposite_king.set_is_short_castle_collision(False)

                if move in opposite_king.valid_moves:
                    opposite_king.valid_moves.remove(move)
                break

    def reset_kings(self):
        self.clear_king_moves()

        w_moves = self.get_initial_king_moves(self.white_king.position)
        b_moves = self.get_initial_king_moves(self.black_king.position)

        self.set_white_king_moves(w_moves)
        self.set_black_king_moves(b_moves)

    def set_white_king_pos(self, pos):
        self.white_king.position = pos
        self.white_king.valid_moves = self.get_initial_king_moves(pos)

    def set_black_king_pos(self, pos):
        self.black_king.position = pos
        self.black_king.valid_moves = self.get_initial_king_moves(pos)

    def is_king(self, piece):
        return piece == "K" or piece == "k"

    def is_long_castling_possible(self):
        if globals.IS_WHITES_TURN:
            return self.white_king.can_long_castle(self.board) and not self.white_king.check

        return self.black_king.can_long_castle(self.board) and not self.black_king.check

    def is_short_castling_possible(self):
        if globals.IS_WHITES_TURN:
            return self.white_king.can_short_castle(self.board) and not self.white_king.check

        return self.black_king.can_short_castle(self.board) and not self.black_king.check

    def get_short_castle_pos(self):
        if globals.IS_WHITES_TURN:
            return self.white_king.get_short_castle_pos()

        return self.black_king.get_short_castle_pos()

    def get_long_castle_pos(self):
        if globals.IS_WHITES_TURN:
            return self.white_king.get_long_castle_pos()

        return self.black_king.get_long_castle_pos()

    def check_and_perform_castling(self, new_pos):
        if new_pos == self.get_long_castle_pos() and self.is_long_castling_possible():
            if globals.IS_WHITES_TURN:
                self.update(Position(new_pos.x, new_pos.y + 1), "R")
            else:
                self.update(Position(new_pos.x, new_pos.y + 1), "r")

            self.update(Position(new_pos.x, new_pos.y - 2), None)
        elif new_pos == self.get_short_castle_pos() and self.is_short_castling_possible():
            if globals.IS_WHITES_TURN:
                self.update(Position(new_pos.x, new_pos.y - 1), "R")
            else:
                self.update(Position(new_pos.x, new_pos.y - 1), "r")

            self.update(Position(new_pos.x, new_pos.y + 1), None)

    def set_board(self, game_board):
        self.board = game_board

    def set_short_castle_possible(self, is_possible, white_king=None, black_king=None):
        if white_king:
            self.white_king.set_is_short_castle_possible(is_possible)
        elif black_king:
            self.black_king.set_is_short_castle_possible(is_possible)

    def set_long_castle_possible(self, is_possible, white_king=None, black_king=None):
        if white_king:
            self.white_king.set_is_long_castle_possible(is_possible)
        elif black_king:
            self.black_king.set_is_long_castle_possible(is_possible)

    # reseting everything when two players propose a rematch and assigning opposite color
    # to a player
    def rematch(self, board):
        globals.IS_WHITES_TURN = True
        globals.FEN_SEQUENCE = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR KQkq"
        globals.ASSIGNED_COLOR = (globals.ASSIGNED_COLOR + 1) % 2
        globals.WHITE_CHECK = False
        globals.BLACK_CHECK = False
        globals.IS_CHECKMATE = False
        globals.IS_STALEMATE = False
        globals.IS_DRAW = False
        globals.OPPONENT_WANTS_REMATCH = False
        globals.IS_THREEFOLD_REPETITION = False
        globals.CURRENT_USER_WANTS_REMATCH = False

        self.white_king = King("K")
        self.black_king = King("k")
        self.white_pawns = Pawns(is_white=True)
        self.black_pawns = Pawns(is_white=False)
        self.clear_moves()

        board.set_fen_sequence(globals.FEN_SEQUENCE)
        self.board = board.get_board_from_fen_sequence(self,  initial_run=True)
        board.show_pieces(self, initial_run=True)

    def is_threefold_repetition(self):
        if len(self.all_moves) >= 3:
            my_dict = {i: self.all_moves.count(i) for i in self.all_moves}
            sorted_dict = sorted(
                my_dict.items(), key=lambda x: x[1], reverse=True)
            return sorted_dict[0][1] == 3

        return False

    def add_move_to_all_moves(self, move):
        self.all_moves.append(move)

    def clear_moves(self):
        self.all_moves.clear()

    def check_for_game_over(self):
        if self.is_white_in_check():
            globals.WHITE_CHECK = True
        if self.is_black_in_check():
            globals.BLACK_CHECK = True

        if self.is_threefold_repetition():
            globals.IS_THREEFOLD_REPETITION = True
            globals.IS_DRAW = True

        if self.is_checkmate():
            globals.IS_CHECKMATE = True

        if self.is_stalemate():
            globals.IS_STALEMATE = True
            globals.IS_DRAW = True
