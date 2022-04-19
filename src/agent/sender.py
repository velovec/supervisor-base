#!/usr/bin/env python3
import event
import json
import pika
import sys

from common import read_agent_id, get_connection


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


def main():
    agent_id = read_agent_id()

    with get_connection() as conn:
        channel = conn.channel()
        while True:
            # transition from ACKNOWLEDGED to READY
            write_stdout('READY\n')

            # read event
            ev = read_event()
            channel.basic_publish(
                exchange='superfleet',
                routing_key='superfleet.server',
                body=json.dumps({
                    "headers": ev.headers,
                    "data": ev.data
                }),
                properties=pika.BasicProperties(headers={
                    "agent-id": agent_id
                })
            )

            # transition from READY to ACKNOWLEDGED
            write_stdout('RESULT 2\nOK')


if __name__ == "__main__":
    main()
