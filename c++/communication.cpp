// communication.cpp
#include <mpi.h>
#include <stdio.h>
#include "trip_data.h"
#include "message.h"
#include "communication.h"  // Dołącz plik nagłówkowy


void send_to_all(thread_data_t *data, const char* message, int clock)
{
    if (data == NULL) {
        fprintf(stderr, "Error: data pointer is NULL\n");
        return;
    }

    if (message == NULL || message[0] == '\0') {
        fprintf(stderr, "Error: message is NULL or empty\n");
        return;
    }

    custom_message_t message_send;
    clock = increment_local_clock(data, clock);

    message_send.clock = clock;
    snprintf(message_send.message, sizeof(message_send.message), "%s", message);
    message_send.sender_rank = data->rank;

    for (int i = 0; i < data->size; i++)
    {
        if (i != data->rank)
        {
            int mpi_err = MPI_Send(&message_send, sizeof(custom_message_t), MPI_BYTE, i, 0, MPI_COMM_WORLD);
            if (mpi_err != MPI_SUCCESS) {
                char error_string[256];
                int length_of_error_string;
                MPI_Error_string(mpi_err, error_string, &length_of_error_string);
                fprintf(stderr, "MPI_Send failed: %s\n", error_string);
            }

            printf("Proces %d (Sender): Wysłałem wiadomość \"%s\" do %d, Zegar: %d\n",
                   data->rank, message_send.message, i, message_send.clock);
        }
    }
}

void send(thread_data_t *data, int index, const char* message)
{
    custom_message_t message_send;
    int clock = *(data->logical_clock);
    clock = increment_local_clock(data, clock);

    message_send.clock = clock;
    snprintf(message_send.message, sizeof(message_send.message), "%s", message);
    message_send.sender_rank = data->rank;

    MPI_Send(&message_send, sizeof(custom_message_t), MPI_BYTE, index, 0, MPI_COMM_WORLD);
    printf("Proces %d (Sender): Wysłałem wiadomość \"%s\" do %d, Zegar: %d\n",
           data->rank, message_send.message, index, message_send.clock);
}

int increment_local_clock(thread_data_t *data, int clock)
{
    pthread_mutex_lock(data->mutex);
    clock++;
    *(data->logical_clock) = clock;
    pthread_mutex_unlock(data->mutex);
    return clock;
}
