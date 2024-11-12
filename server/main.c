#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <windows.h>
#include <time.h>

#pragma comment(lib, "ws2_32.lib")

const char *ASSIGN_COLOR = "ASSIGN_COLOR";
const char *DISCONNECT_USER = "DISCONNECT_USER";
const char *OPPONENT_DISCONNECTED = "OPPONENT_DISCONNECTED";
const char *OPPONENT_CONNECTED = "OPPONENT_CONNECTED";
const char *IS_OPPONENT_CONNECTED = "IS_OPPONENT_CONNECTED";
const char *OPPONENT_CONNECTING = "OPPONENT_CONNECTING";
const char *REMATCH = "REMATCH";
const char *CAN_USER_CONNECT = "CAN_USER_CONNECT";

struct cln {
    SOCKET cfd;
    struct sockaddr_in caddr;
};

struct User {
    int gameId;
    SOCKET cfd;
    int color;
    bool isConnected;
    bool wantsRematch;
    struct sockaddr_in caddr;  // Added client address
};

typedef struct {
    int id;
    struct User users[2];
    int userIdturn;
} Game;

Game *games;

#define MAX_USERS 6
#define MAX_GAMES (MAX_USERS / 2)

void generateNewGame(int gameId) {
    Game game;
    game.id = gameId;
    int color = rand() % 2;

    game.users[0].color = color;
    game.users[1].color = (color + 1) % 2;
    game.userIdturn = (color == 1) ? 0 : 1;
    game.users[0].isConnected = false;
    game.users[1].isConnected = false;
    game.users[0].wantsRematch = false;
    game.users[1].wantsRematch = false;

    games[gameId] = game;
}

DWORD WINAPI cthread(LPVOID arg) {
    struct cln *c = (struct cln *)arg;
    int currentUserId;
    int gameId = -1;

    for (int i = 0; i < MAX_GAMES; i++) {
        if (games[i].users[0].isConnected && !games[i].users[1].isConnected) {
            gameId = i;
            currentUserId = 1;
            games[i].users[1].cfd = c->cfd;
            games[i].users[1].caddr = c->caddr;  // Store client address
            break;
        }
    }

    if (gameId == -1) {
        for (int i = 0; i < MAX_GAMES; i++) {
            if (!games[i].users[0].isConnected && !games[i].users[1].isConnected) {
                gameId = i;
                currentUserId = 0;
                games[i].users[0].cfd = c->cfd;
                games[i].users[0].caddr = c->caddr;  // Store client address
                break;
            }
        }
    }

    char query[128];
    int userRequest = 0;

    while (1) {
        memset(query, 0, sizeof(query));

        if ((userRequest = recv(c->cfd, query, sizeof(query) - 1, 0)) == SOCKET_ERROR || userRequest == 0) {
            break;
        }

        query[userRequest] = '\0';

        if (strcmp(query, CAN_USER_CONNECT) == 0) {
            int ok = (gameId == -1) ? 0 : 1;
            char isOk[2] = { '0' + ok, '\0' };

            send(c->cfd, isOk, strlen(isOk), 0);

            if (ok == 0) {
                break;
            }
        } else if (strcmp(query, ASSIGN_COLOR) == 0) {
            int color = games[gameId].users[currentUserId].color;
            char colorStr[2];
            sprintf(colorStr, "%d", color);

            send(c->cfd, colorStr, strlen(colorStr), 0);
            games[gameId].users[currentUserId].isConnected = true;
        } else if (strcmp(query, IS_OPPONENT_CONNECTED) == 0) {
            int opponentId = (currentUserId + 1) % 2;
            struct User opponent = games[gameId].users[opponentId];

            if (opponent.isConnected) {
                send(c->cfd, OPPONENT_CONNECTED, strlen(OPPONENT_CONNECTED), 0);
                send(opponent.cfd, OPPONENT_CONNECTED, strlen(OPPONENT_CONNECTED), 0);
            } else {
                send(c->cfd, OPPONENT_CONNECTING, strlen(OPPONENT_CONNECTING), 0);
            }
        } else if (strcmp(query, DISCONNECT_USER) == 0) {
            int opponentId = (currentUserId + 1) % 2;
            struct User opponent = games[gameId].users[opponentId];

            send(opponent.cfd, OPPONENT_DISCONNECTED, strlen(OPPONENT_DISCONNECTED), 0);
            games[gameId].users[currentUserId].isConnected = false;

            break;
        } else if (strcmp(query, REMATCH) == 0) {
            int opponentId = (currentUserId + 1) % 2;
            struct User opponent = games[gameId].users[opponentId];

            games[gameId].users[currentUserId].wantsRematch = true;

            send(opponent.cfd, REMATCH, strlen(REMATCH), 0);

            if (opponent.wantsRematch) {
                if (games[gameId].users[currentUserId].color == 0) {
                    games[gameId].userIdturn = currentUserId;
                    games[gameId].users[currentUserId].color = 1;
                    games[gameId].users[opponentId].color = 0;
                } else {
                    games[gameId].userIdturn = (currentUserId + 1) % 2;
                    games[gameId].users[currentUserId].color = 0;
                    games[gameId].users[opponentId].color = 1;
                }
                games[gameId].users[currentUserId].wantsRematch = false;
                games[gameId].users[opponentId].wantsRematch = false;

                printf("Rematch started between clients %s and %s.\n",
                    inet_ntoa(c->caddr.sin_addr),  // For current user
                    inet_ntoa(games[gameId].users[opponentId].caddr.sin_addr)  // For opponent's address
                );
            }
        } else if (games[gameId].users[0].isConnected && games[gameId].users[1].isConnected && strcmp(query, "") != 0) {
            int turn = games[gameId].userIdturn;
            games[gameId].userIdturn = 1 - turn;

            send(games[gameId].users[turn].cfd, query, strlen(query), 0);
        }
    }

    int opponentId = (currentUserId + 1) % 2;
    struct User opponent = games[gameId].users[opponentId];

    if (!opponent.isConnected && !games[gameId].users[currentUserId].isConnected) {
        generateNewGame(gameId);
    }

    closesocket(c->cfd);
    free(c);

    return 0;
}

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
    games = (Game *)malloc(sizeof(Game) * MAX_GAMES);

    int opt = 1;
    SOCKET sfd = socket(AF_INET, SOCK_STREAM, 0);
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt));

    struct sockaddr_in saddr;
    saddr.sin_family = AF_INET;
    saddr.sin_addr.s_addr = INADDR_ANY;
    saddr.sin_port = htons(5050);

    bind(sfd, (struct sockaddr *)&saddr, sizeof(saddr));
    listen(sfd, MAX_GAMES + 100);
    srand((unsigned int)time(NULL));

    for (int i = 0; i < MAX_GAMES; i++) {
        generateNewGame(i);
    }

    printf("Server is running and waiting for connections...\n");

    while (1) {
        struct cln *c = (struct cln *)malloc(sizeof(struct cln));
        int caddrlen = sizeof(c->caddr);

        c->cfd = accept(sfd, (struct sockaddr *)&c->caddr, &caddrlen);
        if (c->cfd == INVALID_SOCKET) {
            printf("Error in accepting client connection.\n");
            free(c);
            continue;
        }

        printf("Client connected from %s\n", inet_ntoa(c->caddr.sin_addr));
        CreateThread(NULL, 0, cthread, (LPVOID)c, 0, NULL);
    }

    closesocket(sfd);
    WSACleanup();
    free(games);
    return 0;
}
