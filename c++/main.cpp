#include <mpi.h>
#include <pthread.h>
#include "trip_data.h"  // Załączenie pliku nagłówkowego
#include "sender.h"  // Implementacja wysyłania
#include "listener.h"  // Implementacja nasłuchiwania

int main(int argc, char** argv) {
    int provided;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_MULTIPLE, &provided);

    if (provided < MPI_THREAD_MULTIPLE) {
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    int rank, size;
    pthread_t sender_thread_id, listener_thread_id;
    pthread_mutex_t mutex;
    pthread_mutex_init(&mutex, NULL);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Zmienna wspólna
    bool want_enter_cs = false;
    int logical_clock = 0, request_clock = 0;

    // Tworzymy strukturę danych
    thread_data_t data;
    data.rank = rank;
    data.size = size;
    data.group_size = 2;  // Przykładowa wartość
    data.group_number = 2;  // Przykładowa wartość
    data.want_enter_cs = &want_enter_cs;
    data.logical_clock = &logical_clock;
    data.request_clock = &request_clock;
    data.mutex = &mutex;

    // Tworzenie wątków
    if (pthread_create(&sender_thread_id, NULL, sender_function, (void*)&data) != 0) {
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    if (pthread_create(&listener_thread_id, NULL, listener_function, (void*)&data) != 0) {
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Czekamy na zakończenie wątków
    pthread_join(sender_thread_id, NULL);
    pthread_join(listener_thread_id, NULL);

    // Sprzątanie
    pthread_mutex_destroy(&mutex);
    MPI_Finalize();

    return 0;
}
