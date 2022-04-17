import json
import threading
import queue

import pika

from event import Event
from xmlrpc.client import ServerProxy


class Agent(threading.Thread):

    def __init__(self, agent_id, conn):
        self.agent_id = agent_id
        self.event_queue = queue.Queue()
        self.handlers = {}
        self.running = True

        self.amqp_conn = conn
        self.rpc_client = ServerProxy('http://supervisor:P%40ssw0rd@localhost:9001/RPC2')

        super().__init__()

    def is_running(self) -> bool:
        return self.running

    def queue_event(self, event: Event) -> None:
        self.event_queue.put(event)

    def on_message(self, ch, method_frame, properties, body):
        command = json.loads(body)

        response = self.rpc_client.__request(command["method"], command["params"])
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            body=json.dumps(response),
            properties=pika.BasicProperties(headers={
                "agent-id": self.agent_id
            })
        )
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self):
        channel = self.amqp_conn.channel()
        channel.queue_declare(queue="superfleet.agent-%s" % self.agent_id, auto_delete=True)
        channel.basic_consume("superfleet.agent-%s" % self.agent_id, self.on_message)

        while self.is_running():
            try:
                event = self.event_queue.get(False)

                channel.basic_publish(
                    exchange='',
                    routing_key='superfleet.server',
                    body=json.dumps({
                        "headers": event.headers,
                        "data": event.data
                    }),
                    properties=pika.BasicProperties(headers={
                        "agent-id": self.agent_id
                    })
                )
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
