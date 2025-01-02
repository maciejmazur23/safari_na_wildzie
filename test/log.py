def info(message, thread_number):
    message = message + '\n'
    with open(f'../log/P_{thread_number}.log', 'a') as file:
        file.write(message)


def reset(thread_number):
    with open(f'../log/P_{thread_number}.log', 'w') as file:
        pass


def append_to_cs(message):
    message = message + '\n'
    with open("../log/cs.txt", "a") as file:
        file.write(message)


def reset_cs():
    with open('../log/cs.txt', 'w') as file:
        pass
