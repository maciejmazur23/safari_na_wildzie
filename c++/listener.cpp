#include <mpi.h>
#include <stdio.h>
#include <unistd.h>
#include <iostream>
#include <pthread.h>
#include "message.h"
#include "trip_data.h"
#include "communication.h"
#include <vector>
#include <tuple>
#include <algorithm> // Dla sortowania

void update_local_clock(thread_data_t *data, int received_clock);

void *listener_function(void *arg)
{
    thread_data_t *data = (thread_data_t *)arg; // Rzutowanie wskaźnika na odpowiedni typ
    custom_message_t message_recv;
    MPI_Status status;

    std::vector<int> received_replays;            // Lista intów
    std::vector<std::tuple<int, int>> requesters; // Lista krotek (int, int)
    std::vector<int> trip_squat;                  // Lista intów

    bool enter_cs = false;
    bool acquires_send = false;
    bool need_more_accepts = false;
    bool trip_processed = false;
    bool accept_send = false;
    int accept_send_id = -1;
    int flag = 0;

    while (1)
    {
        for (int i = 0; i < data->size; i++)
        {
            if (i != data->rank)
            {
                MPI_Iprobe(i, 0, MPI_COMM_WORLD, &flag, &status);
                if (flag)
                {
                    MPI_Recv(&message_recv, sizeof(custom_message_t), MPI_BYTE, i, 0, MPI_COMM_WORLD, &status);
                    printf("Proces %d (Listener): Otrzymałem wiadomość od %d: %s, Zegar: %d\n",
                           data->rank, status.MPI_SOURCE, message_recv.message, message_recv.clock);

                    update_local_clock(data, message_recv.clock);

                    if (strncmp(message_recv.message, "REQUEST", 7) == 0)
                    {
                        requesters.push_back(std::make_tuple(i, message_recv.clock));

                        if (enter_cs)
                        {
                            if (enter_cs && !accept_send)
                            {
                                if (requesters.size() >= (data->group_size - 1)) // Używamy requesters.size()
                                {
                                    std::sort(requesters.begin(), requesters.end(), [](const std::tuple<int, int> &a, const std::tuple<int, int> &b)
                                              { return (std::get<1>(a) < std::get<1>(b)) || (std::get<1>(a) == std::get<1>(b) && std::get<0>(a) < std::get<0>(b)); });

                                    std::cout << "Sorted list: ";
                                    for (const auto &elem : requesters)
                                    {
                                        std::cout << "(" << std::get<0>(elem) << ", " << std::get<1>(elem) << ") ";
                                    }
                                    std::cout << std::endl;

                                    for (int i = 0; i < (data->group_size - 1); i++)
                                    {
                                        auto elem = requesters.front();
                                        requesters.erase(requesters.begin()); // Usuwamy pierwszy element
                                        send(data, std::get<0>(elem), "ACQUIRE");
                                    }

                                    acquires_send = true;
                                }
                                else
                                {
                                    acquires_send = false;
                                }
                            }
                            if (enter_cs && need_more_accepts)
                            {
                                send(data, i, "ACQUIRE");
                            }
                        }
                        else
                        {
                            int request_clock = *(data->request_clock);
                            bool want = *(data->want_enter_cs);
                            if (!want || request_clock == 0)
                            {
                                send(data, i, "ACK");
                            }
                            else if (message_recv.clock < request_clock || (message_recv.clock == request_clock && i < data->rank))
                            {
                                send(data, i, "ACK");
                            }
                        }
                    }

                    // Obsługuje różne inne wiadomości
                    if (strncmp(message_recv.message, "ACK", 5) == 0)
                    {
                        if (accept_send && accept_send_id == i)
                        {
                            accept_send = false;
                        }

                        if (std::find(received_replays.begin(), received_replays.end(), i) == received_replays.end())
                        {
                            received_replays.push_back(i);
                        }
                        std::cout << "[" << *(data->logical_clock) << "] P_" << data->rank
                                  << " received REPLAY from P_" << i
                                  << ". Total replays: ";
                        for (const auto &replay : received_replays)
                        {
                            std::cout << replay << " ";
                        }
                        std::cout << std::endl;

                        if (!enter_cs && received_replays.size() == (data->size - std::min(data->group_number, static_cast<int>(data->size / data->group_size))))
                        {
                            std::cout << "[" << *(data->logical_clock) << "] ";
                            for (const auto &requester : requesters)
                            {
                                std::cout << "(" << std::get<0>(requester) << ", " << std::get<1>(requester) << ") ";
                            }
                            std::cout << std::endl;

                            enter_cs = true;
                            printf("Proces %d (Listener): Wchodzę do sekcji krytycznej\n", data->rank);

                            // Sprawdź, czy liczba elementów w `requesters` spełnia wymóg
                            if (requesters.size() >= (data->group_size - 1))
                            {
                                std::sort(requesters.begin(), requesters.end(),
                                          [](const std::tuple<int, int> &a, const std::tuple<int, int> &b)
                                          {
                                              return (std::get<1>(a) < std::get<1>(b)) ||
                                                     (std::get<1>(a) == std::get<1>(b) && std::get<0>(a) < std::get<0>(b));
                                          });

                                std::cout << "Sorted list: ";
                                for (const auto &elem : requesters)
                                {
                                    std::cout << "(" << std::get<0>(elem) << ", " << std::get<1>(elem) << ") ";
                                }
                                std::cout << std::endl;

                                for (int i = 0; i < (data->group_size - 1); i++)
                                {
                                    auto elem = requesters.front();
                                    requesters.erase(requesters.begin()); // Usuwamy pierwszy element
                                    send(data, std::get<0>(elem), "ACQUIRE");
                                }

                                acquires_send = true;
                            }
                            else
                            {
                                acquires_send = false;
                            }

                            std::cout << "[" << *(data->logical_clock) << "] Acquires send? "
                                      << acquires_send << ", ";
                            for (const auto &requester : requesters)
                            {
                                std::cout << "(" << std::get<0>(requester) << ", " << std::get<1>(requester) << ") ";
                            }
                            std::cout << std::endl;
                        }
                    }
                    if (strncmp(message_recv.message, "ACQUIRE", 7) == 0)
                    {
                        if (!enter_cs && data->want_enter_cs && !accept_send)
                        {
                            send(data, i, "ACCEPT");
                            accept_send = true;
                            accept_send_id = i;
                        }
                        else
                        {
                            send(data, i, "REJECT");
                        }
                    }
                    if (strncmp(message_recv.message, "ACCEPT", 6) == 0)
                    {
                        trip_squat.push_back(i);
                        if (trip_squat.size() == (data->group_size - 1))
                        {

                            enter_cs = false;

                            pthread_mutex_lock(data->mutex);
                            *(data->want_enter_cs) = false;
                            pthread_mutex_unlock(data->mutex);

                            send_to_all(data, "ACK", *(data->logical_clock));

                            trip_processed = true;
                        }
                        else
                        {
                            trip_processed = false;
                        }

                        if (trip_processed)
                        {
                            received_replays.clear();
                            requesters.clear();
                            trip_squat.clear();
                            acquires_send = false;
                            need_more_accepts = false;
                        }
                    }
                    if (strncmp(message_recv.message, "REJECT", 6) == 0)
                    {
                        std::cout << "[" << *(data->logical_clock) << "] - [";
                        for (const auto &req : requesters)
                        {
                            std::cout << "(" << std::get<0>(req) << ", " << std::get<1>(req) << ") ";
                        }
                        std::cout << "]" << std::endl;

                        if (requesters.size() > 0)
                        {
                            auto elem = requesters.front(); // elem to std::tuple<int, int>
                            int index = std::get<0>(elem);
                            requesters.erase(requesters.begin());

                            send(data, index, "ACQUIRE");
                            need_more_accepts = false;
                        }
                        else
                        {
                            need_more_accepts = true;
                        }
                    }
                }
            }
        }
    }
    return NULL;
}

void update_local_clock(thread_data_t *data, int received_clock)
{
    pthread_mutex_lock(data->mutex);
    if (received_clock > *(data->logical_clock))
    {
        *(data->logical_clock) = received_clock + 1;
    }
    else
    {
        (*(data->logical_clock))++;
    }
    pthread_mutex_unlock(data->mutex);
}
