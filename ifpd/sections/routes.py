"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import bottle as bot  # type: ignore
from typing import Dict


class Routes:
    """Routes class."""

    # Empty routes dictionary
    data: Dict = {}

    def __init__(self):
        """
        Create new routes here using the add_route method.
        """

        # Static files ---------------------------------------------------------

        route = "/<dname:re:(css|js|fonts|images|documents)>/<path>"
        self.add_route("static_file", "route", route)

        route = "/documents/<path>/mimetype/<mt1>/<mt2>"
        self.add_route("static_raw_file_download", "route", route)

        # Pages ----------------------------------------------------------------

        self.add_route("home", "route", "/")
        self.add_route("home", "view", "home.tpl.html")

        # Errors ---------------------------------------------------------------

        self.add_route("error404", "error", 404)
        self.add_route("error500", "error", 500)

        return

    def add_route(self, k, t, v):
        """Create a new route or add data to an existing one.

        Args:
                k (string): route name, identical to the route function.
                t (string): the data type (route|view|get|post|error).
                v (string|int): the data value.
        """

        # Create a new route if it does not exist
        if k not in self.data.keys():
            self.data[k] = {}

        # Update existing route
        self.data[k][t] = v

        # Output
        return

    # Pages --------------------------------------------------------------------

    def home(routes, self):
        """Default home-page.

        Args:
                self (App): ProbeDesigner.App instance.
        """
        d = self.vd.copy()
        d["title"] = "Default Home-page"
        d["description"] = "Nothing to say..."
        return d

    # Static files -------------------------------------------------------------

    def static_file(routes, self, dname, path):
        """Access static files.

        Args:
                self (App): ProbeDesigner.App instance.
                dname (string): file type.
                path (string): file name.
        """
        return bot.static_file(path, "%s/%s/" % (self.local_path, dname))

    def static_raw_file_download(routes, self, path, mt1, mt2):
        """Download raw static files.

        Args:
                self (App): ProbeDesigner.App instance.
                path (string): file name.
                mt1 (string): first part of the mimetype.
                mt2 (string): second part of the mimetype.
        """
        ipath = "%s/documents/" % self.local_path
        mt = "%s/%s" % (mt1, mt2)
        return bot.static_file(path, ipath, mimetype=mt)

    # Error --------------------------------------------------------------------

    def error404(routes, self, error):
        """Error 404.

        Args:
                self (App): ProbeDesigner.App instance.
                error: error data.
        """
        return "ERROR 404: nothing here, sorry :("

    def error500(routes, self, error):
        """Error 500.

        Args:
                self (App): ProbeDesigner.App instance.
                error: error data.
        """
        return "ERROR 500: nothing here, sorry :("
