#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include "trip_data.h"
#include "message.h"

// Deklaracja funkcji
int increment_local_clock(thread_data_t *data, int clock);

// Prototypy innych funkcji
void send_to_all(thread_data_t *data, const char* message, int clock);
void send(thread_data_t *data, int index, const char* message);

#endif // COMMUNICATION_H
