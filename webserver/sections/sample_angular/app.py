#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Angular sample sub-section
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import logging

from .. import app
from .routes import Routes

# CLASSES ======================================================================

class App(app.App):
	'''Pool Design Bottle App.

	Args:
		base_dir (string): section base directory.
		route_list (string): sample_angular.routes.Routes instance.
		tprefix (string): title prefix.
	'''
	
	vd = {}
	route_list = Routes()
	base_dir = 'sample_angular'
	tprefix = 'Angular sample ~ '

	def __init__(self, spath, root_path, root_uri, app_uri):
		'''Initialize.

		Args:
			spath (string): sections relative path.
			root_path (string): webserver root absolute path.
			root_uri (string): root webserver url.
			app_uri (string): section relative url.
		'''

		# Run default initialization
		super(App, self).__init__()

		# Save input parameters
		self.spath = spath
		self.root_uri = root_uri
		self.app_uri = app_uri
		self.local_path = root_path + spath + self.base_dir
		self.vpath = self.local_path + '/views/'
		self.qpath = self.local_path + '/query/'

		# Start setting up view dictionary
		self.vd['app_uri'] = root_uri + app_uri
		self.vd['root_uri'] = root_uri
		self.vd['vpath'] = self.vpath
		self.vd['description'] = 'Angular sample section.'

		# Logging config
		logging.basicConfig(level = logging.DEBUG,
			format = '(%(threadName)-9s) %(message)s')

		# Build routes
		self.build_routes()

		# Output
		return

# END ==========================================================================

################################################################################
