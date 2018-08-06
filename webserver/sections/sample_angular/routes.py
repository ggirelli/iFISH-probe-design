#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Oligopool-design Route manager
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import bottle as bot
from .. import routes

# CLASSES ======================================================================

class Routes(routes.Routes):
	'''Routes class.'''

	# Empty routes dictionary
	data = {}

	def __init__(self):
		'''
		Create new routes here using the add_route method.
		'''

		# Set default Routes
		super(Routes, self).__init__()

		# Static files ---------------------------------------------------------

		route = '/jsm/<path:re:.*>'
		self.add_route('node_module', 'route', route)

		# Pages ----------------------------------------------------------------

		# Forms ----------------------------------------------------------------

		# Errors ---------------------------------------------------------------

		# App ------------------------------------------------------------------
		
		self.add_route('get_app', 'route', '/app/<path>')
		return

	# Static files -------------------------------------------------------------

	def node_module(routes, self, path):
		'''Node module content.

		Args:
			routes (Route): sections.Route instance.
			self (App): sections.App instance.
			path (string): filepath.
		'''
		return(bot.static_file(path, self.local_path + '/js/node_modules/'))

	# Pages --------------------------------------------------------------------

	def home(routes, self):
		'''Home-page.

		Args:
			routes (Route): sections.Route instance.
			self (App): sections.App instance.
		'''

		# Template dictionary
		d = self.vd

		# Page title and description
		d['title'] = self.tprefix + 'Home'

		# Local stylesheets
		d['custom_stylesheets'] = ['home.css']

		# Root stylesheets
		d['custom_root_stylesheets'] = []
		
		return(d)

	# Form reception -----------------------------------------------------------

	# Error --------------------------------------------------------------------
	
	# App ----------------------------------------------------------------------

	def get_app(routes, self, path):
		'''Home-page.

		Args:
			routes (Route): sections.Route instance.
			self (App): sections.App instance.
			path (String): file path.
		'''
		return(bot.static_file(path, self.local_path + '/js/app/'))

# END ==========================================================================

################################################################################
