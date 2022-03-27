import time


class Agent:

    def __init__(self, server_url):
        self.server_url = server_url

    def __get_tasks(self):
        pass

    def run(self):
        while True:
            self.__get_tasks()
            time.sleep(5)
