import random
import threading
import time

from mpi4py import MPI

import log

logical_clock = 0
want_to_get_into_CS = False
lock = threading.Lock()


def init_comm():
    """Inicjalizuje komunikację MPI i zwraca komunikator oraz rangi procesów."""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    return comm, rank, size


def enter_critical_section(rank):
    """Symulacja wejścia do sekcji krytycznej."""
    with lock:
        log.info(f"P_{rank} Wchodzi do sekcji krytycznej! Clock:[{logical_clock}]", rank)
        with open("../log/cs.txt", "a") as plik:
            plik.write(str(rank))


def send_request_to_all(comm, rank, size):
    """Wysyła żądanie do wszystkich innych procesów z zegarem logicznym."""
    message = f"REQUEST {rank}"
    # increment_clock()
    for i in range(size):
        if i != rank:
            log.info(f"P_{rank} '{message}' -> P_{i} Clock:[{logical_clock}]", rank)
            comm.send((message, logical_clock), dest=i)


def send_replay(comm, rank, p_i):
    """Wysyła REPLAY do turysty ubiegającego się do CS"""

    message = f"REPLAY {rank}"

    log.info(f"P_{rank} '{message}' -> P_{p_i} Clock:[{logical_clock}]", rank)

    comm.send((message, logical_clock), dest=p_i)


def increment_clock(clock=0):
    global logical_clock
    with lock:
        log.info(f"P_{rank} Clock:[{logical_clock}] before", rank)
        if clock == 0:
            logical_clock += 1
        else:
            logical_clock = clock
        log.info(f"P_{rank} Clock:[{logical_clock}] after", rank)


def trying_to_get_into_CS():
    global logical_clock, want_to_get_into_CS
    with lock:
        log.info(f"P_{rank} trying_to_get_into_CS", rank)
        want_to_get_into_CS = True


def replay_all(comm, rank, size):
    """Wysyła REPLAY do wszystkich po wyjściu z CS"""
    message = f"REPLAY {rank}"
    increment_clock()
    for i in range(size):
        if i != rank:
            log.info(f"P_{rank} '{message}' -> P_{i} Clock:[{logical_clock}]", rank)
            comm.send((message, logical_clock), dest=i)


def listener():
    """Wątek nasłuchujący, który odbiera i wyświetla wiadomości oraz odczytuje współdzieloną zmienną."""
    global logical_clock
    received_replays = 0
    logical_clock = 0
    while True:
        for i in range(size):
            if i != rank:
                message, sender_clock = comm.recv(source=i)
                # received_replays += 1
                with lock:
                    log.info(
                        f"P_{rank} odebral '{message}' | My Clock:[{logical_clock}] Sender Clock: [{sender_clock}]",
                        rank)
                    # logical_clock = max(logical_clock, sender_clock) + 1
                    log.info(f"P_{rank} Result clock:[{logical_clock}]", rank)

                if message == f"REQUEST {i}":
                    if not want_to_get_into_CS:
                        send_replay(comm, rank, i)
                    elif (logical_clock > sender_clock) or (logical_clock == sender_clock and i < rank):
                        send_replay(comm, rank, i)
                elif message == f"REPLAY {i}":
                    received_replays += 1
                    log.info(f"P_{rank} received REPLAY from P_{i}| Replays: [{received_replays}]", rank)

        if received_replays == size - 1:
            enter_critical_section(rank)
            replay_all(comm, rank, size)
            received_replays = 0
            send_request_to_all(comm, rank, size)


def sender():
    """Wątek wysyłający wiadomości i modyfikujący współdzieloną zmienną."""
    log.reset(rank)
    log.reset_cs()
    time.sleep(random.randint(0, 2))
    trying_to_get_into_CS()
    send_request_to_all(comm, rank, size)


comm, rank, size = init_comm()

listener_thread = threading.Thread(target=listener)
sender_thread = threading.Thread(target=sender)

listener_thread.start()
sender_thread.start()

sender_thread.join()
listener_thread.join()
