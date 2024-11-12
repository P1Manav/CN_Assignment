from constants import *
import socket
import globals

'''
Class is responsible for handling the communication with the user (sending and receiving data).
When the user connects, the request that checks if there is not already maximum amount of people
connected to the server is being sent.
Afterwards, the client requests for the color to be assigned and if the client is ready
to receive messages from the server, it checks for the requests in an infinite loop.
'''
class Connection:
    def __init__(self, host, port, board, game, popupWindow):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board = board
        self.game = game
        self.popupWindow = popupWindow

    def receive(self):
        while not globals.SERVER_ERROR:
            try:
                response = self.client.recv(128)
                decoded_response = response.decode().strip()

                if decoded_response == "":
                    globals.SERVER_ERROR = True

                elif self.is_command(decoded_response):
                    self.check_command(decoded_response)

                else:
                    globals.OPPONENT_NOT_CONNECTED_YET = False

                    globals.FEN_SEQUENCE = decoded_response
                    self.game.add_move_to_all_moves(globals.FEN_SEQUENCE)
                    self.board.set_fen_sequence(globals.FEN_SEQUENCE)
                    board = self.board.get_board_from_fen_sequence(
                        self.game)
                    self.game.set_board(board)
                    self.board.set_king_valid_moves(self.game)

                    globals.WHITE_CHECK = False
                    globals.BLACK_CHECK = False
                    
                    self.game.check_for_game_over()

                    globals.IS_WHITES_TURN = not globals.IS_WHITES_TURN
            except socket.error as e:
                globals.LOADING = False
                globals.SERVER_ERROR = True

    def send(self, data):
        try:
            self.client.send(str.encode(data))
        except socket.error as e:
            globals.LOADING = False
            globals.SERVER_ERROR = True

    def connect(self):
        try:
            self.client.connect((self.host, self.port))

            self.send(CAN_USER_CONNECT)
            response = self.client.recv(128)
            can_connect = bool(int(response.decode()))

            if can_connect:
                self.send(ASSIGN_COLOR)
                color = self.client.recv(128)
                globals.ASSIGNED_COLOR = int(color.decode())

                self.send(IS_OPPONENT_CONNECTED)
                response = self.client.recv(128).decode()

                if response == OPPONENT_CONNECTED:
                    globals.OPPONENT_NOT_CONNECTED_YET = False
            else:
                globals.NO_ROOMS_LEFT = True
            globals.LOADING = False
 
        except socket.error as e:
            globals.LOADING = False
            globals.SERVER_ERROR = True

    def is_command(self, response):
        return response in [OPPONENT_DISCONNECTED, OPPONENT_CONNECTED, REMATCH]

    def check_command(self, command):
        if command == OPPONENT_DISCONNECTED:
            globals.OPPONENT_DISCONNECTED = True
        elif command == OPPONENT_CONNECTED:
            globals.OPPONENT_NOT_CONNECTED_YET = False
        elif command == REMATCH:
            globals.OPPONENT_WANTS_REMATCH = True

    def disconnect(self):
        self.send(DISCONNECT_USER)

