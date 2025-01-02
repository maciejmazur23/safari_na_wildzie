import threading

import log
from listener import listener
from mpi_init import init_comm
from sender import sender

group_size = 3
group_number = 2


def main():
    comm, rank, number_of_tourists = init_comm()

    listener_thread = threading.Thread(target=listener, args=(comm, rank, number_of_tourists, group_number, group_size),
                                       name="ListenerThread")
    sender_thread = threading.Thread(target=sender, args=(comm, rank, number_of_tourists), name="SenderThread")

    log.reset(rank)

    log.info(f"Starting threads.", rank)
    listener_thread.start()
    sender_thread.start()

    listener_thread.join()
    sender_thread.join()
    log.info(f"Threads {rank} finished execution.", rank)


main()
