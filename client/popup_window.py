import pygame
from constants import *
from position import Position
import os
import globals

'''
Class is responsible for showing the user informations about the course of the game (draw, checkmate, user disconnecting, user connecting)
or server errors and loading screens.
'''
class PopupWindow:
    def __init__(self, surface):
        self.surface = surface

        self.small_font_size = 20
        self.normal_font_size = 24
        self.big_font_size = 32

        self.small_font = pygame.font.SysFont(
            "calibri", self.small_font_size, bold=True)
        self.normal_font = pygame.font.SysFont(
            "calibri", self.normal_font_size, bold=True)
        self.big_font = pygame.font.SysFont(
            "calibri", self.big_font_size, bold=True)

    def display_waiting_for_opponent(self):
        popup_window_size = Position(320, 240)
        window_text = ["Waiting for the opponent", "to connect"]
        window_name = []
        text_coordinates = []

        for line in window_text:
            window_line = self.small_font.render(line, True, BLACK)
            window_name.append(window_line)
            text_coordinates.append(window_line.get_rect())

        popup_window_coordinates = Position(WINDOW_SIZE / 2 - popup_window_size.x / 2,
                                            WINDOW_SIZE / 2 - popup_window_size.y / 2)

        window_size = pygame.Rect(popup_window_coordinates.x, popup_window_coordinates.y,
                                  popup_window_size.x, popup_window_size.y)

        pygame.draw.rect(self.surface, WHITE, window_size, border_radius=16)

        for i, line in enumerate(window_name):
            text_coordinates[i].center = (WINDOW_SIZE / 2,
                                          WINDOW_SIZE / 2 + (i - 2) * 28 + 40)
            self.surface.blit(line, text_coordinates[i])

    def display_server_disconnected(self, clicked_pos=None):
        error_text = "Server disconnected"
        text = ["Connection to the game ", "has been lost.",
                "Please exit or try again"]
        button_name = ["Exit"]
        self.display(error_text, text, button_name, color=RED)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_name, text)

            if id == 0:
                os._exit(0)

    def display_server_ip_error(self, clicked_pos=None):
        error_text = "Error"
        text = ["Server IP address was not", "passed"]
        button_name = ["Exit"]
        self.display(error_text, text, button_name, color=RED)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_name, text)

            if id == 0:
                os._exit(0)

    def display_checkmate(self, connection, clicked_pos=None):
        top_text = "Game over"

        if globals.WHITE_CHECK:
            text = ["Black wins by checkmate"]
        else:
            text = ["White wins by checkmate"]

        button_names = ["Rematch", "Exit"]
        self.display(top_text, text, button_names, color=BLUE)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_names, text)

            if id == 1:
                connection.disconnect()
                os._exit(0)
            elif id == 0:
                globals.CURRENT_USER_WANTS_REMATCH = True
                connection.send(REMATCH)

    def display_draw(self, connection, clicked_pos=None):
        top_text = "Draw"

        if globals.IS_STALEMATE:
            text = ["Game ends because", "of a stalemate."]
        if globals.IS_THREEFOLD_REPETITION:
            text = ["Game ends because of a", "threefold repetition"]

        button_names = ["Rematch", "Exit"]
        self.display(top_text, text, button_names, color=BLUE)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_names, text)

            if id == 1:
                connection.disconnect()
                os._exit(0)
            elif id == 0:
                globals.CURRENT_USER_WANTS_REMATCH = True
                connection.send(REMATCH)

    def display_opponent_disconnected(self, connection, clicked_pos=None):
        top_text = ""

        if not globals.IS_CHECKMATE and not globals.IS_DRAW:
            top_text = "You won!"

        text = ["Opponent has disconnected"]
        button_names = ["Exit"]
        self.display(top_text, text, button_names, color=BLUE)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_names, text)

            if id == 0:
                connection.disconnect()
                os._exit(0)

    def display_no_rooms_left(self, connection, clicked_pos=None):
        top_text = "Error"

        text = ["No rooms left"]
        button_names = ["Exit"]
        self.display(top_text, text, button_names, color=RED)

        if clicked_pos != None:
            id = self.get_button_clicked_id(clicked_pos, button_names, text)

            if id == 0:
                connection.disconnect()
                os._exit(0)

    def display_loading(self):
        popup_window_size = Position(320, 240)
        window_text = "Loading..."

        window_line = self.small_font.render(window_text, True, BLACK)
        text_coordinates = window_line.get_rect()

        popup_window_coordinates = Position(WINDOW_SIZE / 2 - popup_window_size.x / 2,
                                            WINDOW_SIZE / 2 - popup_window_size.y / 2)

        window_size = pygame.Rect(popup_window_coordinates.x, popup_window_coordinates.y,
                                  popup_window_size.x, popup_window_size.y)

        pygame.draw.rect(self.surface, WHITE, window_size, border_radius=16)

        text_coordinates.center = (WINDOW_SIZE / 2,
                                   WINDOW_SIZE / 2)
        self.surface.blit(window_line, text_coordinates)

    def display(self, window_upper_text, message_lst, button_names, color):
        popup_window_size = Position(320, 240)
        window_name = []
        text_coordinates = []

        text = self.big_font.render(window_upper_text, True, WHITE)
        top_line_coords = text.get_rect()

        popup_window_coordinates = Position(WINDOW_SIZE / 2 - popup_window_size.x / 2,
                                            WINDOW_SIZE / 2 - popup_window_size.y / 2)

        window_size = pygame.Rect(popup_window_coordinates.x, popup_window_coordinates.y,
                                  popup_window_size.x, popup_window_size.y)

        pygame.draw.rect(self.surface, WHITE, window_size, border_radius=16)

        top_line_size = [320, 60]
        top_line = pygame.Rect(popup_window_coordinates.x, popup_window_coordinates.y,
                               top_line_size[0], top_line_size[1])

        pygame.draw.rect(self.surface, color, top_line,
                         border_top_right_radius=16, border_top_left_radius=16)

        top_line_coords.center = (WINDOW_SIZE / 2,
                                  top_line.y + top_line_size[1] / 2)
        self.surface.blit(text, top_line_coords)

        for line in message_lst:
            window_line = self.normal_font.render(line, True, BLACK)
            window_name.append(window_line)
            text_coordinates.append(window_line.get_rect())

        for i, line in enumerate(window_name):
            if len(window_name) == 1:
                text_coordinates[i].center = (WINDOW_SIZE / 2,
                                              WINDOW_SIZE / 2)
            else:
                text_coordinates[i].center = (WINDOW_SIZE / 2,
                                              WINDOW_SIZE / 2 + (i - 2) * 28 + 40)
            self.surface.blit(line, text_coordinates[i])

        padding = 72
        if len(message_lst) == 3:
            padding = 56

        if len(button_names) == 2:
            button_size = [120, 40]

            button_position = Position(popup_window_coordinates.x + popup_window_size.x / 4 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)
            self.draw_button(button_position, button_size,
                             color, button_name_text=button_names[0])

            button_position = Position(popup_window_coordinates.x + 3 * popup_window_size.x / 4 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)
            self.draw_button(button_position, button_size,
                             color, button_name_text=button_names[1])

        else:
            button_size = [160, 40]

            button_position = Position(popup_window_coordinates.x + popup_window_size.x / 2 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)
            self.draw_button(button_position, button_size,
                             color, button_name_text=button_names[0])

    def draw_button(self, position, button_size, color, button_name_text):
        button_coords = pygame.Rect(position.x, position.y,
                                    button_size[0], button_size[1])

        pygame.draw.rect(self.surface, color, button_coords, border_radius=16)
        button_name = self.small_font.render(button_name_text, True, WHITE)

        name_coords = button_name.get_rect()
        name_coords.center = (button_size[0] / 2 + position.x,
                              button_size[1] / 2 + position.y)

        self.surface.blit(button_name, name_coords)

    def get_button_clicked_id(self, clicked_pos, button_names, message_lst):
        popup_window_size = Position(320, 240)
        popup_window_coordinates = Position(WINDOW_SIZE / 2 - popup_window_size.x / 2,
                                            WINDOW_SIZE / 2 - popup_window_size.y / 2)

        padding = 72
        if len(message_lst) == 3:
            padding = 56

        if len(button_names) == 2:
            button_size = [120, 40]

            button_position = Position(popup_window_coordinates.x + popup_window_size.x / 4 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)

            if (button_position.x + button_size[0]) > clicked_pos.x > button_position.x and \
                    (button_position.y + button_size[1]) > clicked_pos.y > button_position.y:
                return 0

            button_position = Position(popup_window_coordinates.x + 3 * popup_window_size.x / 4 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)

            if (button_position.x + button_size[0]) > clicked_pos.x > button_position.x and \
                    (button_position.y + button_size[1]) > clicked_pos.y > button_position.y:
                return 1

        else:
            button_size = [160, 40]

            button_position = Position(popup_window_coordinates.x + popup_window_size.x / 2 - button_size[0] / 2,
                                       popup_window_coordinates.y + popup_window_size.y - padding)

            if (button_position.x + button_size[0]) > clicked_pos.x > button_position.x and \
                    (button_position.y + button_size[1]) > clicked_pos.y > button_position.y:
                return 0

        return None
