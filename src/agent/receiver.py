#!/usr/bin/env python3
import json
import pika

from common import read_agent_id, get_connection
from xmlrpc.client import ServerProxy

agent_id = read_agent_id()
rpc_client = ServerProxy('http://supervisor:P%40ssw0rd@localhost:9001/RPC2')


def on_message(ch, method_frame, properties, body):
    command = json.loads(body)

    response = rpc_client.__getattr__(command["method"])(*command["params"])
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response),
        properties=pika.BasicProperties(
            headers={
                "agent-id": agent_id
            },
            correlation_id=properties.correlation_id
        )
    )
    ch.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    with get_connection() as conn:
        channel = conn.channel()

        channel.queue_declare(queue="superfleet.agent-%s" % agent_id, auto_delete=True, exclusive=True)
        channel.queue_bind(queue="superfleet.agent-%s" % agent_id, exchange="superfleet",
                           routing_key="superfleet.agent-%s" % agent_id)
        channel.basic_consume("superfleet.agent-%s" % agent_id, on_message)

        channel.start_consuming()


if __name__ == "__main__":
    main()
