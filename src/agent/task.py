import logger
import threading
import uuid


class Task(threading.Thread):

    def __init__(self, agent, runner, *args, **kwargs):
        self.agent = agent

        self.running = False
        self.finished = False
        self.result = None

        self.task_id = str(uuid.uuid4())
        self.logger = logger.setup_logger("task-%s" % self.task_id)

        self.task = {
            "runner": runner,
            "args": args,
            "kwargs": kwargs
        }

        threading.Thread.__init__(self)

    def run(self):
        self.running = True

        self.logger.info("Starting task...")

        if self.task["runner"]:
            self.result = {
                "id": self.task_id,
                "status": "completed",
                "result": self.task["runner"](
                    self.logger, *self.task["args"], **self.task["kwargs"]
                )
            }
        else:
            self.result['result'] = {
                "id": self.task_id,
                "status": "error",
                "error": "no runner"
            }

        self.logger.info("Task completed with status: %s", self.result["status"])

        self.running = False
        self.finished = True
