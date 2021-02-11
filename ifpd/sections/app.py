"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

import bottle as bot  # type: ignore


class App(bot.Bottle):
    """WebServer section App."""

    def __init__(self):
        """Initialize."""

        # Run default initialization
        super(App, self).__init__()

        # Output
        return

    def __get_proper_rout(self, data, page):
        # Load template if requested
        if "view" in data.keys():

            @self.route(data["route"])
            @bot.view(self.vpath + data["view"])
            def route(**kwargs):
                return getattr(self.route_list, page)(self, **kwargs)

        else:

            @self.route(data["route"])
            def route(**kwargs):
                return getattr(self.route_list, page)(self, **kwargs)

        return route

    def __get_reception(self, data, page):
        @self.get(data["get"])
        def route(**kwargs):
            return getattr(self.route_list, page)(self, **kwargs)

        return route

    def __post_reception(self, data, page):
        @self.post(data["post"])
        def route(**kwargs):
            return getattr(self.route_list, page)(self, **kwargs)

        return route

    def __error_page(self, data, page):
        @self.error(data["error"])
        def route(*args, **kwargs):
            return getattr(self.route_list, page)(self, *args, **kwargs)

        return route

    def route_builder(self, page, data):
        """Generate routes based on route data.

        Args:
                page (string): route name, identical to route function name.
                data (dict): rout data.
        """

        # If a proper route is requested
        if "route" in data.keys():
            route = self.__get_proper_rout(data, page)

        # Get reception
        elif "get" in data.keys():
            route = self.__get_reception(data, page)

        # Post reception
        elif "post" in data.keys():
            route = self.__post_reception(data, page)

        # Error pages
        elif "error" in data.keys():
            route = self.__error_page(data, page)

        else:
            return ()

        return route

    def build_routes(self):
        """Build routes."""

        # Will contain the route functions
        route_functions = {}

        # Build views
        for page in self.route_list.data.keys():
            # Retrieve route function
            route_functions[page] = self.route_builder(page, self.route_list.data[page])
