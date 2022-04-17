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

        response = self.rpc_client.__getattr__(command["method"])(*command["params"])
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            body=json.dumps(response),
            properties=pika.BasicProperties(
                headers={
                    "agent-id": self.agent_id
                },
                correlation_id=properties.correlation_id
            )
        )
        ch.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self):
        channel = self.amqp_conn.channel()
        channel.queue_declare(queue="superfleet.agent-%s" % self.agent_id, auto_delete=True)
        channel.queue_bind(queue="superfleet.agent-%s" % self.agent_id, exchange="superfleet", routing_key="superfleet.agent-%s" % self.agent_id)
        channel.basic_consume("superfleet.agent-%s" % self.agent_id, self.on_message)

        while self.is_running():
            self.amqp_conn.process_data_events(time_limit=0.1)

            while not self.event_queue.empty():
                event = self.event_queue.get()
                channel.basic_publish(
                    exchange='superfleet',
                    routing_key='superfleet.server',
                    body=json.dumps({
                        "headers": event.headers,
                        "data": event.data
                    }),
                    properties=pika.BasicProperties(headers={
                        "agent-id": self.agent_id
                    })
                )

    def stop(self):
        self.running = False
