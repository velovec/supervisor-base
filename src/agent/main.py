#!/usr/bin/env python3

import json
import logger
import os
import requests
import signal
import socket
import timer
import task
import uuid

from selectors import DefaultSelector, EVENT_READ

from xmlrpc.client import ServerProxy


class Agent:

    def __init__(self):
        self.server_url = os.environ.get("COORDINATOR_URL")
        self.socket_pair = socket.socketpair()
        self.running = True

        self.logger = logger.setup_logger("agent")

        if os.path.exists("agent_id"):
            with open("agent_id", 'r') as agent_id:
                self.agent_id = agent_id.read().strip()
        else:
            self.agent_id = str(uuid.uuid4())
            with open("agent_id", 'w') as agent_id:
                agent_id.write(self.agent_id)

        self.threads = []

        self.__start_thread(timer.Timer(self, 5, b'\x01'))
        self.__start_thread(timer.Timer(self, 3, b'\xFF'))

        self.task = None

        self.rpc_client = ServerProxy('http://localhost:9001/RPC2')

    def __start_thread(self, instance):
        instance.start()

        self.threads.append(instance)

    def __stop_thread(self, instance):
        self.threads.remove(instance)

        instance.join()

    def __check_tasks(self):
        if self.task:
            if self.task.finished:
                self.__report_task()
        else:
            task_data = self.__get_task()

            if task:
                self.task = task.Task(self, lambda l, x: {}, task_data)

                self.__start_thread(self.task)

    def __do_post(self, endpoint, data):
        data["agent-id"] = self.agent_id

        return requests.post(self.server_url + endpoint, data=json.dumps(data), headers={
            "Content-Type": "application/json"
        }).json()

    def __report_task(self):
        result = self.task.result
        self.__stop_thread(self.task)
        self.task = None

        self.__do_post("/api/agent/report", data=result)

    def __get_task(self):
        return self.__do_post("/api/agent/task", data={})

    def __heartbeat(self):
        self.__do_post("/api/agent/heartbeat", data={
            "processes": self.rpc_client.supervisor.getAllProcessInfo()
        })

    def __dispatch_action(self, op_code):
        if op_code == b'\x00':
            self.running = False
            return False

        if op_code == b'\x01':
            self.__check_tasks()

        if op_code == b'\xFF':
            self.__heartbeat()

        return True

    def run(self):
        self.logger.info("Starting Agent %s...", self.agent_id)
        signal.signal(signal.SIGINT, self.stop)

        sel = DefaultSelector()
        sel.register(self.socket_pair[0], EVENT_READ)

        self.logger.info("Agent started")
        while self.running:
            for key, _ in sel.select():
                if key.fileobj == self.socket_pair[0]:
                    op_code = self.socket_pair[0].recv(1)

                    if not self.__dispatch_action(op_code):
                        self.logger.warning("Waiting for %d thread(s) termination..." % len(self.threads))
                        for thread in self.threads[:]:
                            self.__stop_thread(thread)

                        self.logger.warning("Terminated")
                        return

    def execute_action(self, op_code=b'\x00'):
        self.socket_pair[1].send(op_code)

    def stop(self, signum, frame):
        self.logger.warning("Terminating...")
        self.execute_action(b'\x00')


if __name__ == "__main__":
    a = Agent()

    a.run()
