#!/usr/bin/env python3

import event
import sys


def write_stdout(s: str) -> None:
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s: str) -> None:
    sys.stderr.write(s)
    sys.stderr.flush()


def read_event() -> event.Event:
    header_line = sys.stdin.readline()
    headers = {x.split(":")[0]: x.split(":")[1] for x in header_line.split()}
    data = sys.stdin.read(int(headers['len']))

    return event.Event(headers=headers, data=data)


def process_event(ev: event.Event) -> bool:
    return True


def main():
    while 1:
        # transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')

        # read event
        ev = read_event()

        # transition from READY to ACKNOWLEDGED
        if process_event(ev):
            write_stdout('RESULT 2\nOK')
        else:
            write_stdout('RESULT 4\nFAIL')


if __name__ == '__main__':
    main()
