import os
import time

from xmlrpc.client import ServerProxy


class Agent:

    def __init__(self, server_url):
        self.server_url = server_url
        self.rpc_client = ServerProxy('http://localhost:9001/RPC2')

    def __get_tasks(self):
        pass

    def run(self):
        while True:
            self.__get_tasks()
            time.sleep(5)


if __name__ == "__main__":
    a = Agent(os.environ.get("SERVER_URL"))
    a.run()
