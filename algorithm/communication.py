import log
from clock import increment_clock, get_logical_clock, set_send_request_clock, lock


def send_request_to_all(comm, rank, number_of_tourists):
    """Wysyła żądanie do wszystkich innych procesów z zegarem logicznym."""
    message = f"REQUEST {rank}"
    increment_clock(rank)
    for i in range(number_of_tourists):
        if i != rank:
            log.info(f"[{get_logical_clock()}] P_{rank} '{message}' -> P_{i}", rank)
            comm.send((message, get_logical_clock()), dest=i)


def send_request(comm, rank, p_i):
    """Wysyła żądanie do wszystkich innych procesów z zegarem logicznym."""
    message = f"REQUEST {rank}"
    increment_clock(rank)
    log.info(f"[{get_logical_clock()}] P_{rank} '{message}' -> P_{p_i}", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_replay(comm, rank, p_i):
    """Wysyła REPLAY do procesu ubiegającego się do CS."""
    message = f"REPLAY {rank}"
    log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_acquire(comm, rank, p_i):
    """Wysyła ACQUIRE do procesu ze swojej listy."""
    message = f"ACQUIRE {rank}"
    log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_accept(comm, rank, p_i):
    """Wysyła ACCEPT do procesu"""
    message = f"ACCEPT {rank}"
    log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_reject(comm, rank, p_i):
    """Wysyła REJECT do procesu"""
    message = f"REJECT {rank}"
    log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def replay_all(comm, rank, number_of_tourists):
    """Wysyła REPLAY do wszystkich po wyjściu z CS."""
    message = f"REPLAY {rank}"
    increment_clock(rank)
    for i in range(number_of_tourists):
        if i != rank:
            log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{i}", rank)
            comm.send((message, get_logical_clock()), dest=i)


def replay_all_from_requesters(comm, rank, requesters):
    """Wysyła REPLAY do wszystkich po wyjściu z CS."""
    log.info(f"REPLAY ALL from: [{requesters}]", rank)
    message = f"REPLAY {rank}"
    increment_clock(rank)
    for i in requesters:
        if i[0] != rank:
            log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{i[0]}", rank)
            comm.send((message, get_logical_clock()), dest=i[0])


def release_all(comm, rank, number_of_tourists, squat):
    """Wysyła REPLAY do wszystkich po wyjściu z CS."""
    message = f"RELEASE {rank} {squat}"
    increment_clock(rank)
    for i in range(number_of_tourists):
        if i != rank:
            log.info(f"[{get_logical_clock()}] P_{rank} sends '{message}' to P_{i}", rank)
            comm.send((message, get_logical_clock()), dest=i)
