import random
import threading
import time

import log
from communication import send_request_to_all
from critical_section import set_want_to_enter_cs

lock = threading.Lock()


def trying_to_get_into_CS(rank):
    log.info("Trying_to_get_into_CS", rank)
    set_want_to_enter_cs(True)


def sender(comm, rank, number_of_tourists):
    """Wątek wysyłający."""
    time.sleep(random.randint(0, 2))
    trying_to_get_into_CS(rank)
    send_request_to_all(comm, rank, number_of_tourists)
