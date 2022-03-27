import os

from agent import Agent

if __name__ == "__main__":

    a = Agent(os.environ.get("SERVER_URL"))

    a.run()
