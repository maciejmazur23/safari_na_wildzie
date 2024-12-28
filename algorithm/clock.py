import threading

import log

logical_clock = 0
lock = threading.Lock()

send_request_clock = 0


def get_send_request_clock():
    return send_request_clock


def set_send_request_clock(rank):
    global logical_clock, send_request_clock
    with lock:
        log.info(f"Set send_request_clock as {logical_clock}", rank)
        send_request_clock = logical_clock


def increment_clock(rank, clock=0):
    """Inkrementuje zegar logiczny."""
    global logical_clock
    with lock:
        before = logical_clock
        logical_clock = clock if clock > 0 else logical_clock + 1
        log.info(f"Clock incremented: [{before}] -> [{logical_clock}]", rank)


def increase_local_clock_after_received_message(message, sender_clock, rank):
    """Aktualizuje lokalny zegar na podstawie odebranej wiadomości."""
    global logical_clock
    with lock:
        logical_clock = max(logical_clock, sender_clock) + 1
        log.info(f"Updated clock after receiving message '{message}': {logical_clock}", rank)


def get_logical_clock():
    return logical_clock
