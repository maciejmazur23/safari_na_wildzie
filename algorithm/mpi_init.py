from mpi4py import MPI

import log


def init_comm():
    """Inicjalizuje komunikację MPI i zwraca komunikator oraz rangi procesów."""

    log.reset_cs()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    return comm, rank, size
