import pygame
from board import Board
from game import Game
from constants import *
import globals
import copy
import threading
from connection import Connection
from popup_window import PopupWindow
from position import Position
import os
import sys

surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
board = Board(surface, globals.FEN_SEQUENCE)

board.draw()
game = Game()
chess_board = board.get_board_from_fen_sequence(game, initial_run=True)
game.set_board(chess_board)
pygame.init()

popupWindow = PopupWindow(surface)
popupWindow.display_loading()
host = ''

if len(sys.argv) == 2:
    host = sys.argv[1]
else:
    globals.SERVER_IP_ERROR = True

port = 5050
connection = Connection(host, port, board, game, popupWindow)

# function updates the game and checks for special moves like en passant capture or castling
def update_game(piece, old_pos, new_pos):
    if game.is_king(piece):
        game.check_and_perform_castling(new_pos)

    game.update(old_pos, None)
    game.update(new_pos, piece)

    is_double_pawn_move = False

    if game.is_pawn(piece):
        if game.is_pawn_double_move(old_pos, new_pos):
            game.set_pawn_double_push(new_pos)
            is_double_pawn_move = True

        opponent_pawn_pos = game.get_opponent_pawn_position()

        if game.is_promotion(new_pos):
            if globals.IS_WHITES_TURN:
                game.update(new_pos, "Q")
            else:
                game.update(new_pos, "q")

        if game.is_en_passant_move(new_pos, opponent_pawn_pos):
            game.update(opponent_pawn_pos, None)

    if game.is_rook(piece):
        game.set_rook_has_moved(old_pos)

    if piece == "k":
        game.set_black_king_pos(new_pos)
        game.set_black_king_has_moved()
    elif piece == "K":
        game.set_white_king_pos(new_pos)
        game.set_white_king_has_moved()

    board.set_king_valid_moves(game)

    if is_double_pawn_move:
        board.convert_board_to_fen_sequence(game, new_pos)
    else:
        board.convert_board_to_fen_sequence(game)

    game.clear_opponent_double_push()

    globals.IS_WHITES_TURN = not globals.IS_WHITES_TURN

    fen_sequence = board.get_fen_sequence()
    game.add_move_to_all_moves(fen_sequence)

    game.check_for_game_over()

    connection.send(fen_sequence)


def display_popups(is_click, mouse_x, mouse_y):
    if globals.SERVER_IP_ERROR:
        if is_click:
            popupWindow.display_server_ip_error(Position(mouse_x, mouse_y))
        else:
            popupWindow.display_server_ip_error()
    elif globals.NO_ROOMS_LEFT:
        if is_click:
            popupWindow.display_no_rooms_left(
                connection, Position(mouse_x, mouse_y))
        else:
            popupWindow.display_no_rooms_left(connection)
    elif globals.SERVER_ERROR:
        if is_click:
            popupWindow.display_server_disconnected(Position(mouse_x, mouse_y))
        else:
            popupWindow.display_server_disconnected()
    elif globals.OPPONENT_DISCONNECTED:
        if is_click:
            popupWindow.display_opponent_disconnected(connection,
                                                      Position(mouse_x, mouse_y))
        else:
            popupWindow.display_opponent_disconnected(connection)
    elif globals.IS_CHECKMATE:
        if is_click:
            popupWindow.display_checkmate(
                connection, Position(mouse_x, mouse_y))
        else:
            popupWindow.display_checkmate(connection)
    elif globals.IS_DRAW:
        if is_click:
            popupWindow.display_draw(
                connection, Position(mouse_x, mouse_y))
        else:
            popupWindow.display_draw(connection)
    elif globals.OPPONENT_NOT_CONNECTED_YET:
        popupWindow.display_waiting_for_opponent()


def main():
    pygame.display.set_caption("Chess")
    MAX_FPS = 60

    pygame.display.flip()

    selected_piece = None
    drop_pos = False
    clock = pygame.time.Clock()

    initial_run = True
    drag_pos = None

    board.show_pieces(game, None, initial_run)
    initial_run = False
    pygame.display.update()

    piece_img = None
    pos = None
    drag = False
    valid_moves = []
    is_click = False

    mouse_x = None
    mouse_y = None

    if not globals.SERVER_IP_ERROR:
        connection.connect()

    if not globals.SERVER_ERROR and not globals.NO_ROOMS_LEFT and not globals.SERVER_IP_ERROR:
        # program receives responses from the server by creating a separate thread
        receive_thread = threading.Thread(target=connection.receive)
        receive_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    connection.disconnect()
                    os._exit(0)

            elif event.type == pygame.QUIT:
                pygame.quit()
                connection.disconnect()
                os._exit(0)

            if event.type == pygame.MOUSEMOTION:
                mouse = event.pos
                mouse_x, mouse_y = mouse
                pos, piece = board.get_row_col_and_piece(
                    mouse_x, mouse_y, game)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos
                valid_moves = []

                mouse_x, mouse_y = mouse
                pos, piece = board.get_row_col_and_piece(
                    mouse_x, mouse_y, game)

                clicked_pos = copy.deepcopy(pos)
                is_click = True

                if piece != None:
                    if globals.IS_WHITES_TURN == piece.isupper() \
                            and piece.isupper() == globals.ASSIGNED_COLOR \
                            and not globals.SERVER_ERROR \
                            and not globals.IS_CHECKMATE \
                            and not globals.IS_DRAW \
                            and not globals.OPPONENT_NOT_CONNECTED_YET:
                        if drag == False:
                            drag_pos = pos
                            piece_img = board.get_image(piece)

                        valid_moves = game.get_valid_moves(pos)
                        drop_pos = True
                        selected_piece = pos, piece
                        drag = True

            elif event.type == pygame.MOUSEBUTTONUP:
                piece_img = None
                drag_pos = None
                drag = False

                if drop_pos:
                    old_pos, piece = selected_piece
                    new_pos, drop_piece = board.get_row_col_and_piece(
                        mouse_x, mouse_y, game)

                    if old_pos != new_pos and new_pos in valid_moves:
                        if drop_piece == None or isinstance(drop_piece, str) and \
                                not (piece.isupper() == drop_piece.isupper()):
                            valid_moves = []
                            globals.WHITE_CHECK = False
                            globals.BLACK_CHECK = False
                            update_game(piece, old_pos, new_pos)

        surface.fill(BLACK)
        board.draw()

        if globals.WHITE_CHECK:
            board.show_check(game, is_white=True)
        elif globals.BLACK_CHECK:
            board.show_check(game, is_white=False)

        board.show_pieces(game, drag_pos)

        if valid_moves != [] and not globals.SERVER_ERROR:
            board.show_valid_moves(valid_moves, game.get_board(), clicked_pos)

        if drag and piece_img != None:
            x = mouse[0] - piece_img.get_height() / 2
            y = mouse[1] - piece_img.get_width() / 2
            surface.blit(piece_img, tuple([x, y]))

        if globals.LOADING:
            popupWindow.display_loading()

        display_popups(is_click, mouse_x, mouse_y)
        is_click = False

        if globals.CURRENT_USER_WANTS_REMATCH and globals.OPPONENT_WANTS_REMATCH and not globals.OPPONENT_DISCONNECTED:
            game.rematch(board)

        pygame.display.update()

        clock.tick(MAX_FPS)


if __name__ == "__main__":
    try:
        if globals.SERVER_IP_ERROR:
            raise Exception("Server IP is not provided or invalid.")
        main()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)
