import log
from clock import increase_local_clock_after_received_message, get_logical_clock, get_send_request_clock
from communication import send_replay, send_acquire, send_accept, send_reject, send_request, replay_all
from critical_section import enter_critical_section, get_want_to_enter_cs, get_enter_cs, start_trip, end_trip, \
    out_critical_section, set_want_to_enter_cs


def listener(comm, rank, number_of_tourists, group_number, group_size):
    """Wątek nasłuchujący."""
    received_replays = []
    requesters = []
    trip_squat = []
    acquires_send = False
    need_more_accepts = False
    while True:
        for i in range(number_of_tourists):
            if comm.Iprobe(source=i):
                message, sender_clock = comm.recv(source=i)
                log.info(f"Message: {message}", rank)
                increase_local_clock_after_received_message(message, sender_clock, rank)

                if message.startswith("REQUEST"):
                    if get_enter_cs():
                        requesters.append((i, sender_clock))
                        if get_enter_cs() and not acquires_send:
                            acquires_send, requesters = send_acquire_to_group(requesters, comm, rank, group_size)
                        if get_enter_cs() and need_more_accepts:
                            acquires_send, requesters = send_acquire_to_group(requesters, comm, rank, group_size)
                    else:
                        requesters = process_request(i, requesters, comm, rank, sender_clock)

                if message.startswith("REPLAY"):
                    received_replays = process_replay_message(i, rank, received_replays)
                    acquires_send, requesters = try_enter_cs(acquires_send, comm, group_number, group_size,
                                                             number_of_tourists, rank, received_replays,
                                                             requesters)

                if message.startswith("ACQUIRE"):
                    process_acquire(comm, rank, i)

                if message.startswith("ACCEPT") and acquires_send:
                    trip_processed = process_accept(trip_squat, rank, i, group_size, comm, number_of_tourists)
                    if trip_processed:
                        received_replays = []
                        requesters = []
                        trip_squat = []
                        acquires_send = False
                        need_more_accepts = False

                if message.startswith("REJECT") and acquires_send:
                    requesters = process_reject(requesters, comm, rank)

                # if message.startswith("RELEASE"):
                #     log.info(f"Before process release {requesters} | {received_replays}", rank)
                #     requesters, trip_squat, received_replays, acquires_send, need_more_accepts = process_release(
                #         requesters, comm, rank, message, trip_squat, received_replays,
                #         acquires_send, need_more_accepts, i)
                #     log.info(f"After process release {requesters} | {received_replays}", rank)


def process_release(requesters, comm, rank, message, trip_squat, received_replays, acquires_send, need_more_accepts,
                    sender_id):
    start = message.find('[')
    end = message.find(']')
    if start != -1 and end != -1:
        substring = message[start + 1:end]

        numbers = substring.split(', ')

        if rank in numbers:
            log.info("number == rank", rank)
            set_want_to_enter_cs(False)
            out_critical_section(rank)
            requesters = []
            trip_squat = []
            received_replays = []
            acquires_send = False
            need_more_accepts = False

        for number in numbers:
            new_requesters = []
            for i, item in enumerate(requesters):
                log.info(f"item: {item} {number} {(int(item[0]) == int(number))}", rank)
                if not ((int(item[0]) == int(number)) or sender_id == int(item[0])):
                    new_requesters.append(item)
                    log.info(f"if {number} new_requesters: {new_requesters}", rank)
                else:
                    log.info(f"else {number}", rank)
                    if item[0] in received_replays:
                        received_replays.remove(item[0])
                    send_request(comm, rank, item[0])

                requesters = new_requesters
    else:
        print("Brak nawiasów [] w ciągu!")

    return requesters, trip_squat, received_replays, acquires_send, need_more_accepts


def try_enter_cs(acquires_send, comm, P, G, T, rank, received_replays, requesters):
    if not get_enter_cs() and len(received_replays) == (T - min(P, int(T / G))):
        log.info(f"[{get_logical_clock()}] {str(requesters)}", rank)
        enter_critical_section(rank)
        acquires_send, requesters = send_acquire_to_group(requesters, comm, rank, G)
        log.info(f"[{get_logical_clock()}] Acquires send? {acquires_send}, {requesters}", rank)
    return acquires_send, requesters


def process_replay_message(i, rank, received_replays):
    received_replays.append(i)
    log.info(f"[{get_logical_clock()}] P_{rank} received REPLAY from P_{i}. Total replays: {received_replays}", rank)
    return received_replays


def process_request(i, requesters, comm, rank, sender_clock):
    requesters.append((i, sender_clock))
    log.info(f"Clock: {get_send_request_clock()} Sender clock: {sender_clock}", rank)
    if not get_want_to_enter_cs() or get_send_request_clock() == 0:
        send_replay(comm, rank, i)
    elif sender_clock < get_send_request_clock() or (sender_clock == get_send_request_clock() and i < rank):
        send_replay(comm, rank, i)
    return requesters


def process_acquire(comm, rank, p_i):
    if not get_enter_cs() and get_want_to_enter_cs():
        send_accept(comm, rank, p_i)
        # enter_critical_section(rank)
    else:
        send_reject(comm, rank, p_i)


def process_accept(trip_squat, rank, p_i, group_size, comm, number_of_tourists):
    trip_squat.append(p_i)
    if len(trip_squat) == group_size - 1:
        process_trip(rank, trip_squat, comm, number_of_tourists)
        return True
    else:
        return False


def process_trip(rank, trip_squat, comm, number_of_tourists):
    start_trip(trip_squat, rank)
    # time.sleep(2)
    end_trip(trip_squat, rank)
    replay_all(comm, rank, number_of_tourists)
    out_critical_section(rank)
    set_want_to_enter_cs(False)
    return [], [], [], False, False


def send_acquire_to_group(requesters, comm, rank, group_size):
    log.info(f"[{get_logical_clock()}] send_acquire_to_group: {requesters}", rank)
    if len(requesters) >= (group_size - 1):
        requesters = list(sorted(requesters, key=lambda x: (x[1], x[0])))
        log.info(f'Sorted list: {requesters}', rank)
        for _ in range((group_size - 1)):
            elem = requesters.pop(0)
            send_acquire(comm, rank, elem[0])
        return True, requesters
    return False, requesters


def process_reject(requesters, comm, rank):
    log.info(f"[{get_logical_clock()}] {str(requesters)}", rank)
    if len(requesters) > 0:
        elem = requesters.pop(0)
        send_acquire(comm, rank, elem[0])
    return requesters
