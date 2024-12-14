import time

import log
from clock import increase_local_clock_after_received_message
from communication import send_replay, send_acquire, send_accept, send_reject
from critical_section import enter_critical_section, get_want_to_enter_cs, get_enter_cs, start_trip, end_trip, \
    out_critical_section


def listener(comm, rank, number_of_tourists, group_number, group_size):
    """Wątek nasłuchujący."""
    received_replays = 0
    requesters = []
    trip_squat = []
    acquires_send = False
    while True:
        for i in range(number_of_tourists):
            if i != rank:
                message, sender_clock = comm.recv(source=i)
                log.info(message, rank)
                increase_local_clock_after_received_message(message, sender_clock, rank)

                if message.startswith("REQUEST"):
                    process_request(i, requesters, comm, rank)
                    if get_enter_cs() and not acquires_send:
                        acquires_send = send_acquire_to_group(requesters, comm, rank, group_size)
                elif message.startswith("REPLAY"):
                    received_replays = process_replay_message(i, rank, received_replays)
                elif message.startswith("ACQUIRE"):
                    process_acquire(comm, rank, i)
                elif message.startswith("ACCEPT") and acquires_send:
                    trip_started = process_accept(trip_squat, rank, i, group_size)
                    if trip_started:
                        return
                elif message.startswith("REJECT") and acquires_send:
                    process_reject(requesters, comm, rank)

                if not get_enter_cs() and received_replays == (number_of_tourists - group_number):
                    log.info(str(requesters), rank)
                    enter_critical_section(rank)
                    acquires_send, requesters = send_acquire_to_group(requesters, comm, rank, group_size)
                    log.info(f"Acquires send? {acquires_send}, {requesters}", rank)


def process_replay_message(i, rank, received_replays):
    received_replays += 1
    log.info(f"P_{rank} received REPLAY from P_{i}. Total replays: {received_replays}", rank)
    return received_replays


def process_request(i, requesters, comm, rank):
    requesters.append(i)
    log.info(f"P_{rank} processed request from P_{i}", rank)
    if not get_want_to_enter_cs() and not get_enter_cs():
        send_replay(comm, rank, i)
    elif i > rank and not get_enter_cs():
        send_replay(comm, rank, i)


def process_acquire(comm, rank, p_i):
    if not get_enter_cs():
        send_accept(comm, rank, p_i)
    else:
        send_reject(comm, rank, p_i)


def process_accept(trip_squat, rank, p_i, group_size):
    trip_squat.append(p_i)
    if len(trip_squat) == group_size - 1:
        start_trip(trip_squat, rank)
        time.sleep(3)
        end_trip(rank)
        out_critical_section(rank)
        return True
    else:
        return False


def send_acquire_to_group(requesters, comm, rank, group_size):
    log.info(f"send_acquire_to_group: {requesters}", rank)
    if len(requesters) >= (group_size - 1):
        requesters = sorted(requesters, reverse=True)
        for _ in range((group_size - 1)):
            i = requesters.pop(0)
            send_acquire(comm, rank, i)
            log.info(f"send_acquire_to_group: {requesters}", rank)
        return True, requesters
    log.info(f"send_acquire_to_group: {requesters}", rank)
    return False, requesters


def process_reject(requesters, comm, rank):
    log.info(str(requesters), rank)
    i = requesters.pop(0)
    send_acquire(comm, rank, i)
