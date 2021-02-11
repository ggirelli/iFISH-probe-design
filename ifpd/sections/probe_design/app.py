"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from ifpd.sections import app as rootApp
from ifpd.sections.probe_design.enquirer import Enquirer
from ifpd.sections.probe_design.queue import Queue
from ifpd.sections.probe_design.routes import Routes
import logging
from typing import Dict


class App(rootApp.App):
    """Probe Design Bottle App.

    Args:
            app_uri (string): section relative url.
            base_dir (string): section base directory.
            consumer (Enquirer): queue consumer.
            local_path (string): absolute path to app directory.
            qpath (string): absolute path to query folder.
            queue (Queue): query queue.
            root_path (string): webserver root absolute path.
            root_uri (string): root webserver url.
            route_list (string): probe_design.routes.Routes instance.
            section_path (string): sections relative path.
            tprefix (string): title prefix.
            vd (string): view data.
            vpath (string): absolute path to views folder.
            BUF_SIZE (int): queue size.
    """

    vd: Dict = {}
    route_list = Routes()
    base_dir = "probe_design"
    tprefix = "Probe Designer ~ "
    vd = {}
    BUF_SIZE = 0
    MAX_CURR = 1

    def __init__(
        self,
        section_path,
        static_path,
        root_path,
        root_uri,
        app_uri,
        MAX_CURR=None,
        BUF_SIZE=None,
    ):
        """Initialize.

        Args:
                section_path (string): sections relative path.
                root_path (string): webserver root absolute path.
                root_uri (string): root webserver url.
                app_uri (string): section relative url.
                MAX_CURR (int): maximum number of running tasks.
                BUF_SIZE (int): queue size, defaults to 0.
        """

        # Run default initialization
        super(App, self).__init__()

        # Save input parameters
        self.section_path = section_path
        self.root_uri = root_uri
        self.app_uri = app_uri
        self.local_path = "%s%s" % (section_path, self.base_dir)
        self.static_path = static_path
        self.vpath = "%s/views/" % self.local_path
        self.qpath = "%s/query/" % self.static_path
        self.MAX_CURR = MAX_CURR
        self.BUF_SIZE = BUF_SIZE

        # Start setting up view dictionary
        self.vd["app_uri"] = "%s%s" % (root_uri, app_uri)
        self.vd["root_uri"] = root_uri
        self.vd["vpath"] = self.vpath
        self.vd["qpath"] = self.qpath
        self.vd["description"] = "iFISH probe designer application."
        self.vd["breadcrumbs"] = False
        self.vd["menu_template"] = None
        self.vd["SHOW_COOKIE_CONSENT_BANNER"] = False
        self.vd["google_analytics_token"] = ""

        # Set default
        if not type(None) == type(MAX_CURR):
            self.MAX_CURR = MAX_CURR
        if not type(None) == type(BUF_SIZE):
            self.BUF_SIZE = BUF_SIZE

        # Logging config
        logging.basicConfig(
            level=logging.DEBUG, format="(%(threadName)-9s) %(message)s"
        )

        # Initialize queue
        self.queue = Queue(BUF_SIZE=self.BUF_SIZE, MAX_CURR=self.MAX_CURR)
        self.consumer = Enquirer(self.queue)
        self.consumer.start()

        # Save queue
        self.vd["queue"] = self.queue

        # Build routes
        self.build_routes()

        # Output
        return
