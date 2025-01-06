// message.h
#ifndef MESSAGE_H
#define MESSAGE_H

#include <mpi.h>

#define MAX_MESSAGE_LEN 100

// Struktura wiadomości
typedef struct {
    char message[MAX_MESSAGE_LEN]; // Wiadomość (np. REQUEST, REPLY)
    int clock;                     // Zegar logiczny nadawcy
    int sender_rank;               // Numer procesu wysyłającego
} custom_message_t;

#endif // MESSAGE_H
