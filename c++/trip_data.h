// trip_data.h
#ifndef TRIP_DATA_H
#define TRIP_DATA_H

#include <mpi.h>
#include <pthread.h>

// Struktura przechowująca wszystkie zmienne potrzebne w wątkach
typedef struct {
    int rank;
    int size;
    int group_size;
    int group_number;
    bool *want_enter_cs;
    int *logical_clock;
    int *request_clock;
    pthread_mutex_t *mutex;
} thread_data_t;

#endif // TRIP_DATA_H