from mpi4py import MPI
import random
import time
import os

# Constants
group_size = 3
guide_count = 2
delay = 1
NOREQ = 9999
max_possible_rank = 8

# Global Variables
my_rank = None
my_clock = 0
ack_count = 0
after = []
group = []
chef = False
doing_stuff_at_dembiec_pkm = False
asking_for_crit = False
inJured = False
awaiting_recv = False
startTime = -1
s = time.time()
request = None
status = None

# MPI setup
comm = MPI.COMM_WORLD
my_rank = comm.Get_rank()
size = comm.Get_size()


# Helper functions
def debug(fmt, *args):
    print(f"{my_clock:4} P{my_rank} " + fmt % args)


def queue_string(q):
    return "[" + ", ".join(map(str, q)) + "]"


def dog(q):
    return "[" + ", ".join(map(str, q)) + "]"


# Struct-like classes
class ElemQ:
    def __init__(self, pid, reqTime):
        self.pid = pid
        self.reqTime = reqTime


class Packet:
    def __init__(self, tag, time, reqTime=NOREQ, myGroup=None):
        if myGroup is None:
            myGroup = [-1] * group_size
        self.tag = tag
        self.time = time
        self.reqTime = reqTime
        self.myGroup = myGroup


# MPI communication functions
def send_message(destination, tag, reqTime=NOREQ):
    pkg = Packet(tag, my_clock, reqTime)
    if tag in [2, 3]:  # START or RELEASE
        pkg.myGroup = group
    comm.send(pkg, dest=destination)


def recv_message():
    global awaiting_recv
    if not awaiting_recv:
        request = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        awaiting_recv = True
    status = request.Test()  # Test returns True if message is ready
    if status:
        src = request.source
        pkg = request.recv()  # Receive the actual message
        awaiting_recv = False
        return src, pkg
    return None, None


def update_lamport(update_clock=0):
    global my_clock
    my_clock = max(my_clock, update_clock) + 1


def sortFunc(a, b):
    return a.reqTime < b.reqTime or (a.reqTime == b.reqTime and a.pid < b.pid)


def RESP(t):
    global ack_count, after, doing_stuff_at_dembiec_pkm
    src, pkg = recv_message()
    if pkg is None:
        return

    update_lamport(pkg.time)

    if pkg.tag == 0 and not doing_stuff_at_dembiec_pkm:
        eval = (pkg.time == t and src < my_rank) or (pkg.time < t)
        after.append(ElemQ(src, pkg.reqTime))
        after.sort(key=lambda x: (x.reqTime, x.pid))

        if (eval and asking_for_crit and not doing_stuff_at_dembiec_pkm) or (
                not doing_stuff_at_dembiec_pkm and not asking_for_crit):
            update_lamport()
            send_message(src, 1)  # ACK

    elif pkg.tag == 1 and not doing_stuff_at_dembiec_pkm:
        if pkg.reqTime > startTime:
            ack_count += 1

    elif pkg.tag == 3:  # RELEASE
        debug("Removing group members: %s", dog(pkg.myGroup))
        for pid in pkg.myGroup:
            after = [e for e in after if e.pid != pid]
        debug("After removing: %s", queue_string([e.pid for e in after]))
        if doing_stuff_at_dembiec_pkm and src in group:
            doing_stuff_at_dembiec_pkm = False


def WANT():
    global ack_count, asking_for_crit
    update_lamport()
    t = my_clock
    ack_count = 0
    for rank in range(size):
        if rank != my_rank:
            send_message(rank, 0, t)

    asking_for_crit = True
    while ack_count < size - group_size * guide_count and len(after) < group_size - 1:
        RESP(t)
        time.sleep(delay)

    after.append(ElemQ(my_rank, t))
    after.sort(key=lambda x: (x.reqTime, x.pid))
    asking_for_crit = False


def FREE():
    global after
    update_lamport()
    for e in after:
        send_message(e.pid, 1)  # ACK


def GROUP():
    global after
    # Przypisanie wartości, jeśli 'after' nie jest jeszcze zainicjalizowana
    if 'after' not in globals():
        after = []  # Przykład inicjalizacji pustą listą, zależnie od kontekstu

    pos = next((i for i, e in enumerate(after) if e.pid == my_rank), -1)
    if pos == -1:
        debug("Error: Process not in queue!")
        return

    if (pos + 1) % group_size == 0:
        debug("I am the chef!")
        group = [e.pid for e in after[pos - group_size + 1:pos + 1]]
        debug("My group: %s", queue_string(group))
        for u in group:
            send_message(u, 2)  # START
        chef = True
        doing_stuff_at_dembiec_pkm = True

    if time.time() - s > 12:
        debug("Shuffling queue...")
        random.shuffle(after)

    src, pkg = recv_message()
    if pkg is None:
        return

    if pkg.tag == 2:  # START
        global startTime
        startTime = my_clock
        debug("Started, my group: %s", dog(pkg.myGroup))
        group.extend(pkg.myGroup)
        doing_stuff_at_dembiec_pkm = True

    elif pkg.tag == 3:  # RELEASE
        for pid in pkg.myGroup:
            after = [e for e in after if e.pid != pid]
        debug("After removing: %s", queue_string([e.pid for e in after]))


def main():
    global group, doing_stuff_at_dembiec_pkm, chef, inJured

    debug("My rank %d (max rank %d)", my_rank, size)

    while True:
        debug("Waiting for turn...")
        WANT()
        debug("Searching for group, current queue: %s", queue_string([e.pid for e in after]))
        s = time.time()
        while not doing_stuff_at_dembiec_pkm:
            GROUP()
            time.sleep(delay)

        if chef:
            debug("I am the chef!")

        debug("Taking a break...")
        start = time.time()
        while time.time() - start < 5:
            pass

        if chef:
            debug("Sending release...")
            for i in range(size):
                send_message(i, 3)  # RELEASE
            chef = False

        while doing_stuff_at_dembiec_pkm:
            RESP(NOREQ)

        group.clear()
        debug("Return to normal...")
        FREE()

        if random.randint(0, 99) > 50:
            inJured = True
            debug("I am injured!")

        start = time.time()
        while inJured and time.time() - start < 5:
            RESP(NOREQ)
        inJured = False


if __name__ == "__main__":
    main()
