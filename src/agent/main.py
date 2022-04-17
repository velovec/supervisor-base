#!/usr/bin/env python3
import event
import os
import pika
import sys
import uuid

from agent import Agent


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


def read_agent_id() -> str:
    if os.path.exists("agent-id"):
        with open("agent-id", 'r') as agent_id:
            return agent_id.read().strip()
    else:
        agent_uuid = str(uuid.uuid4())
        with open("agent-id", 'w') as agent_id:
            agent_id.write(agent_uuid)
        return agent_uuid


def main():
    parameters = pika.ConnectionParameters(
        host="amqp.velovec.pro", port=5673,
        credentials=pika.credentials.PlainCredentials(
            "publisher", "AuthT0ken"
        )
    )

    with pika.BlockingConnection(parameters=parameters) as conn:
        agent_id = read_agent_id()
        agent = Agent(agent_id, conn)
        agent.setDaemon(True)
        agent.start()

        while agent.is_running():
            # transition from ACKNOWLEDGED to READY
            write_stdout('READY\n')

            # read event
            ev = read_event()

            # transition from READY to ACKNOWLEDGED
            agent.queue_event(ev)
            write_stdout('RESULT 2\nOK')

        agent.join()


if __name__ == "__main__":
    main()
