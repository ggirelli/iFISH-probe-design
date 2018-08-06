#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Probe-design sub-section
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import logging

from .. import app as rootApp
from .enquirer import Enquirer
from .queue import Queue
from .routes import Routes

# CLASSES ======================================================================

class App(rootApp.App):
	'''Probe Design Bottle App.

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
		spath (string): sections relative path.
		tprefix (string): title prefix.
		vd (string): view data.
		vpath (string): absolute path to views folder.
		BUF_SIZE (int): queue size.
	'''
	
	vd = {}
	route_list = Routes()
	base_dir = 'probe_design'
	tprefix = 'Probe Designer ~ '
	vd = {}
	BUF_SIZE = 0
	MAX_CURR = 1

	def __init__(self, spath, root_path, root_uri, app_uri,
		MAX_CURR = None, BUF_SIZE = None):
		'''Initialize.

		Args:
			spath (string): sections relative path.
			root_path (string): webserver root absolute path.
			root_uri (string): root webserver url.
			app_uri (string): section relative url.
			MAX_CURR (int): maximum number of running tasks.
			BUF_SIZE (int): queue size, defaults to 0.
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
		self.MAX_CURR = MAX_CURR
		self.BUF_SIZE = BUF_SIZE

		# Start setting up view dictionary
		self.vd['app_uri'] = root_uri + app_uri
		self.vd['root_uri'] = root_uri
		self.vd['vpath'] = self.vpath
		self.vd['description'] = 'Probe designer application, '
		self.vd['description'] += 'to design FISH probes.'

		# Set default
		if not type(None) == type(MAX_CURR):
			self.MAX_CURR = MAX_CURR
		if not type(None) == type(BUF_SIZE):
			self.BUF_SIZE = BUF_SIZE

		# Logging config
		logging.basicConfig(level = logging.DEBUG,
			format = '(%(threadName)-9s) %(message)s')

		# Initialize queue
		self.queue = Queue(BUF_SIZE = self.BUF_SIZE, MAX_CURR = self.MAX_CURR)
		self.consumer = Enquirer(self.queue)
		self.consumer.start()

		# Save queue
		self.vd['queue'] = self.queue

		# Build routes
		self.build_routes()

		# Output
		return

# END ==========================================================================

################################################################################
