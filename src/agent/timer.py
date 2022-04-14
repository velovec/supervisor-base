import logger
import threading
import time


class Timer(threading.Thread):

    def __init__(self, agent, interval, op_code):
        self.agent = agent

        self.interval = interval
        self.op_code = op_code
        self.logger = logger.setup_logger("timer-%02x" % ord(self.op_code))

        threading.Thread.__init__(self)

    def run(self):
        self.logger.info("Started timer for opCode(%02X) with interval %d" % (ord(self.op_code), self.interval))

        tick = 0
        while self.agent.running:
            if tick == 0:
                self.agent.execute_action(self.op_code)

            tick += 1
            if tick >= self.interval:
                tick = 0

            time.sleep(1)

        self.logger.info("Timer for opCode(%02X) stopped" % ord(self.op_code))
