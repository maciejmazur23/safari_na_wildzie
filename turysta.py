import queue
import random
import threading
import time

from mpi4py import MPI

message_queue = queue.Queue()

logical_clock = 0
lock = threading.Lock()


def init_comm():
    """Inicjalizuje komunikację MPI i zwraca komunikator oraz rangi procesów."""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    return comm, rank, size


def enter_critical_section(rank):
    """Symulacja wejścia do sekcji krytycznej."""
    print(f"P_{rank} Wchodzi do sekcji krytycznej!")


def receive_messages(comm, rank, size):
    """Nasłuchuje na wiadomości od innych procesów i aktualizuje zegar logiczny."""
    global logical_clock
    received_messages = 0

    for i in range(size):
        if i != rank:
            message, sender_clock = comm.recv(source=i)
            print(f"P_{rank} odebral '{message}' od P_{i} z zegarem {sender_clock}")

            with lock:
                logical_clock = max(logical_clock, sender_clock) + 1

            if message == f"REQUEST {i}":
                print(f"P_{rank} send REPLAY to P_{i}")
                send_replay(comm, rank, i)
            elif message == f"REPLAY {i}":
                print(f"P_{rank} received REPLAY from P_{i}")
                received_messages += 1
                print(f"{rank} received_messages: {received_messages}")

    return received_messages


def send_request_to_all(comm, rank, size):
    """Wysyła żądanie do wszystkich innych procesów z zegarem logicznym."""

    message = f"REQUEST {rank}"

    increment_clock()

    for i in range(size):
        if i != rank:
            print(f"P_{rank} '{message}' -> P_{i}")
            comm.send((message, logical_clock), dest=i)


def send_replay(comm, rank, p_i):
    """Wysyła REPLAY do turysty ubiegającego się do CS"""

    message = f"REPLAY {rank}"

    print(f"P_{rank} '{message}' -> P_{p_i}")

    comm.send((message, logical_clock), dest=p_i)


def increment_clock(clock=0):
    global logical_clock
    with lock:
        if clock == 0:
            logical_clock += 1
        else:
            logical_clock = clock


def listener():
    """Wątek nasłuchujący, który odbiera i wyświetla wiadomości oraz odczytuje współdzieloną zmienną."""
    r = 0
    while True:
        # r = receive_messages(comm, rank, size)
        for i in range(size):
            if i != rank:
                message, sender_clock = comm.recv(source=i)
                r += 1
                print(f"P_{rank} dostal '{message}' r: {r}")
        if r == 2:
            enter_critical_section(rank)
            break

    """ działa
     r = 0
     while True:
         # r = receive_messages(comm, rank, size)
         for i in range(size):
             print(f"P_{rank} for {i}")
             if i != rank:
                 message, sender_clock = comm.recv(source=i)
                 r += 1
                 print(f"P_{rank} dostal '{message}' r: {r}")
         if r == 2:
             enter_critical_section(rank)
             break"""


def sender():
    """Wątek wysyłający wiadomości i modyfikujący współdzieloną zmienną."""
    time.sleep(random.randint(0, 5))
    send_request_to_all(comm, rank, size)

    # increment_clock()
    # send_request_to_all(comm, rank, size)

    """ działa
        for i in range(size):
        if rank != i:
            send_replay(comm, rank, i)
    """


comm, rank, size = init_comm()

listener_thread = threading.Thread(target=listener)
sender_thread = threading.Thread(target=sender)

listener_thread.start()
sender_thread.start()

sender_thread.join()
listener_thread.join()
