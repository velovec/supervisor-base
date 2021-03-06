import os
import uuid
import pika

parameters = pika.ConnectionParameters(
    host="amqp.velovec.pro", port=5673,
    credentials=pika.credentials.PlainCredentials(
        "publisher", "AuthT0ken"
    ), heartbeat=1800,
    connection_attempts=1024, retry_delay=1,
    socket_timeout=1800, stack_timeout=1900
)


def get_connection():
    return pika.BlockingConnection(parameters=parameters)


def read_agent_id() -> str:
    if os.path.exists("agent-id"):
        with open("agent-id", 'r') as agent_id:
            return agent_id.read().strip()
    else:
        agent_uuid = str(uuid.uuid4())
        with open("agent-id", 'w') as agent_id:
            agent_id.write(agent_uuid)
        return agent_uuid
