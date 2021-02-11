"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import configparser
import os


class Query(object):
    """Single query class."""

    def __init__(self, query_id, query_root):
        super(Query, self).__init__()
        assert Query.exists(query_id, query_root), f'query "{query_id}" not found.'

        self.data = {}
        self.data["id"] = query_id
        with open(os.path.join(query_root, f"{query_id}.config"), "r") as IH:
            config = configparser.ConfigParser()
            config.read_string("".join(IH.readlines()))
            self.data.update(config["GENERAL"].items())
            self.data.update(config["WHEN"].items())
            self.data.update(config["WHERE"].items())
            self.data.update(config["WHAT"].items())
            self.data.update(config["HOW"].items())

    @staticmethod
    def exists(query_id, query_root):
        """Check if a query exists."""
        # dirExists = os.path.isdir(os.path.join(query_root, query_id))
        configExists = os.path.isfile(os.path.join(query_root, f"{query_id}.config"))
        return configExists  # and dirExists
