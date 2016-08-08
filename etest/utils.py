import sys
import socket

def normalize(string):
    """ Deletes spaces and uppercases the string """
    if string[-1] == '.':
        string2 = string[:-1]
    else:
        string2 = string
    return string2.replace(" ", "").upper()


def run_with_dev_server():
    return 'manage.py' in sys.argv[0]


def run_on_dev_machine():
    return socket.gethostname() == 'hrutr'