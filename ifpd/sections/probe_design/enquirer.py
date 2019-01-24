#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Probe-design Queue consumer (database enquirer)
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import configparser
import datetime
import logging
import os
import subprocess as sp
import threading
import time

# CLASSES ======================================================================

class Enquirer(threading.Thread):
	'''Database enquirer.'''

	def __init__(self, queue):
		'''Instance method.

		Args:
			queue (Queue): Queue object which will contain the queries.
		'''

		# Initializer
		super(Enquirer, self).__init__()

		# Set class vars
		self.queue = queue

		# Close
		return

	def run(self):
		'''Run one query from the queue.'''

		while True:
			if not self.queue.empty():
				cmd = self.queue.get()

				# If the queue released a task
				if not type(None) == type(cmd):
					query_id = os.path.basename(cmd[3])

					config = configparser.ConfigParser()
					with open(f'{cmd[3]}.config', 'r') as IH:
						config.read_string("".join(IH.readlines()))

					logging.debug(f'Running query "{query_id}"')
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()
					config['GENERAL']['status'] = 'running'
					config['GENERAL']['start_time'] = f'{timestamp}'
					config['GENERAL']['start_isotime'] = isotimestamp
					with open(f'{cmd[3]}.config', 'w+') as OH:
						config.write(OH)
					sp.call(cmd)
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()

					logging.debug(f'Finished query "{query_id}"')
					config['GENERAL']['status'] = 'done'
					config['GENERAL']['done_time'] = f'{timestamp}'
					config['GENERAL']['done_isotime'] = isotimestamp
					with open(f'{cmd[3]}.config', 'w+') as OH:
						config.write(OH)
					cmd = self.queue.task_done(cmd)

		return

# END ==========================================================================

################################################################################
