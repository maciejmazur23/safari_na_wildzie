import log
from clock import increment_clock, get_logical_clock


def send_request_to_all(comm, rank, number_of_tourists):
    """Wysyła żądanie do wszystkich innych procesów z zegarem logicznym."""
    message = f"REQUEST {rank}"
    increment_clock(rank)
    for i in range(number_of_tourists):
        if i != rank:
            log.info(f"P_{rank} '{message}' -> P_{i}. Clock: [{get_logical_clock()}]", rank)
            comm.send((message, get_logical_clock()), dest=i)


def send_replay(comm, rank, p_i):
    """Wysyła REPLAY do procesu ubiegającego się do CS."""
    message = f"REPLAY {rank}"
    log.info(f"P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_acquire(comm, rank, p_i):
    """Wysyła ACQUIRE do procesu ze swojej listy."""
    message = f"ACQUIRE {rank}"
    log.info(f"P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_accept(comm, rank, p_i):
    """Wysyła ACCEPT do procesu"""
    message = f"ACCEPT {rank}"
    log.info(f"P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def send_reject(comm, rank, p_i):
    """Wysyła REJECT do procesu"""
    message = f"REJECT {rank}"
    log.info(f"P_{rank} sends '{message}' to P_{p_i}.", rank)
    comm.send((message, get_logical_clock()), dest=p_i)


def replay_all(comm, rank, number_of_tourists):
    """Wysyła REPLAY do wszystkich po wyjściu z CS."""
    message = f"REPLAY {rank}"
    increment_clock(rank)
    for i in range(number_of_tourists):
        if i != rank:
            log.info(f"P_{rank} sends '{message}' to P_{i}. Clock: [{get_logical_clock()}]", rank)
            comm.send((message, get_logical_clock()), dest=i)
