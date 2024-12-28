import threading

import clock
import log

lock = threading.Lock()

want_to_enter_cs = False
enter_cs = False
trip_started = False


def get_trip_started():
    return trip_started


def start_trip(squat, thread_number):
    global trip_started
    with lock:
        log.info(f'Trip started with {str(squat)} processes', thread_number)
        trip_started = True


def end_trip(squat, thread_number):
    global trip_started
    with lock:
        log.info(f'Trip ended with {str(squat)} processes', thread_number)
        trip_started = False


def get_want_to_enter_cs():
    return want_to_enter_cs


def set_want_to_enter_cs(true_or_false):
    global want_to_enter_cs
    with lock:
        want_to_enter_cs = true_or_false


def get_enter_cs():
    return enter_cs


def set_enter_cs(true_or_false):
    global enter_cs
    with lock:
        enter_cs = true_or_false


def enter_critical_section(rank):
    """Symulacja wejścia do sekcji krytycznej."""
    global enter_cs
    with lock:
        enter_cs = True
        log.info(f"P_{rank} enters critical section. Clock: [{clock.get_logical_clock()}]", rank)
        log.info("{", rank)
        log.append_to_cs(str(rank))


def out_critical_section(rank):
    """Symulacja wyjścia z sekcji krytycznej."""
    global enter_cs, want_to_enter_cs
    with lock:
        log.info(f"P_{rank} out critical section. Clock: [{clock.get_logical_clock()}]", rank)
        enter_cs = False
        want_to_enter_cs = False
        log.info("}", rank)
