#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Oligopool-design sub-section
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import bottle as bot

# CLASSES ======================================================================

class App(bot.Bottle):
	'''WebServer section App.'''

	def __init__(self):
		'''Initialize.'''

		# Run default initialization
		super(App, self).__init__()

		# Output
		return

	def route_builder(self, page, data):
		'''Generate routes based on route data.

		Args:
			page (string): route name, identical to route function name.
			data (dict): rout data.
		'''

		# If a proper route is requested
		if 'route' in data.keys():
			
			# Load template if requested
			if 'view' in data.keys():
				@self.route(data['route'])
				@bot.view(self.vpath + data['view'])
				def route(**kwargs):
					return(getattr(self.route_list, page)(self, **kwargs))
			else:
				@self.route(data['route'])
				def route(**kwargs):
					return(getattr(self.route_list, page)(self, **kwargs))

		# Get reception
		elif 'get' in data.keys():
			@self.get(data['get'])
			def route(**kwargs):
				return(getattr(self.route_list, page)(self, **kwargs))

		# Post reception
		elif 'post' in data.keys():
			@self.post(data['post'])
			def route(**kwargs):
				return(getattr(self.route_list, page)(self, **kwargs))

		# Error pages
		elif 'error' in data.keys():
			@self.error(data['error'])
			def route(*args, **kwargs):
				return(getattr(self.route_list, page)(self, *args, **kwargs))

		else:
			return()

		return(route)

	def build_routes(self):
		'''Build routes.'''

		# Will contain the route functions
		route_functions = {}

		# Build views
		for page in self.route_list.data.keys():
			# Retrieve route function
			route_functions[page] = self.route_builder(page,
				self.route_list.data[page])

# END ==========================================================================

################################################################################
