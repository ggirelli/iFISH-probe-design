"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import configparser
import datetime
import logging
import os
import subprocess as sp
import threading
import time


class Enquirer(threading.Thread):
    """Database enquirer."""

    def __init__(self, queue):
        """Instance method.

        Args:
                queue (Queue): Queue object which will contain the queries.
        """

        # Initializer
        super(Enquirer, self).__init__()

        # Set class vars
        self.queue = queue

        # Close
        return

    def readQueryConfig(self, queryDir):
        config = configparser.ConfigParser()
        with open(f"{queryDir}.config", "r") as IH:
            config.read_string("".join(IH.readlines()))
        return config

    def writeQueryConfig(self, queryDir, config):
        with open(f"{queryDir}.config", "w+") as OH:
            config.write(OH)

    def __get_outdir_id(self, cmd):
        return 5

    def run(self):
        """Run one query from the queue."""

        while True:
            if not self.queue.empty():
                cmd = self.queue.get()

                # If the queue released a task
                if not type(None) == type(cmd):
                    logging.info(cmd)
                    outdir_id = self.__get_outdir_id(cmd)

                    query_id = os.path.basename(cmd[outdir_id])
                    logging.info((cmd[outdir_id], query_id))
                    EH = open(f"{cmd[outdir_id]}.error.log", "w+")
                    logging.info(EH)

                    logging.debug(f'Running query "{query_id}"')
                    timestamp = time.time()
                    isotimestamp = datetime.datetime.fromtimestamp(
                        timestamp
                    ).isoformat()
                    config = self.readQueryConfig(cmd[outdir_id])
                    config["GENERAL"]["status"] = "running"
                    config["WHEN"]["start_time"] = f"{timestamp}"
                    config["WHEN"]["start_isotime"] = isotimestamp
                    self.writeQueryConfig(cmd[outdir_id], config)

                    sp.call(cmd, stderr=EH)
                    timestamp = time.time()
                    isotimestamp = datetime.datetime.fromtimestamp(
                        timestamp
                    ).isoformat()
                    logging.debug(f'Finished query "{query_id}"')
                    config = self.readQueryConfig(cmd[outdir_id])
                    config["GENERAL"]["status"] = "done"
                    config["WHEN"]["done_time"] = f"{timestamp}"
                    config["WHEN"]["done_isotime"] = isotimestamp
                    self.writeQueryConfig(cmd[outdir_id], config)
                    cmd = self.queue.task_done(cmd)
                    EH.close()

        return
