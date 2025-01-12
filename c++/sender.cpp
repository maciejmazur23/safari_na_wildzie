#include <mpi.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include "message.h"
#include "trip_data.h"
#include "communication.h"

void* sender_function(void* arg) {
    thread_data_t *data = (thread_data_t*)arg;  // Rzutowanie wskaźnika na odpowiedni typ

    while (1) {
        if (*(data->want_enter_cs)) {
            continue;
        }

        pthread_mutex_lock(data->mutex);
        *(data->want_enter_cs) = true;
        pthread_mutex_unlock(data->mutex);

        int request_clock = *(data->logical_clock);
        pthread_mutex_lock(data->mutex);
        *(data->request_clock) = (request_clock + 1);
        pthread_mutex_unlock(data->mutex);

        send_to_all(data, "REQUEST", request_clock);

        sleep(1);
    }
    return NULL;
}