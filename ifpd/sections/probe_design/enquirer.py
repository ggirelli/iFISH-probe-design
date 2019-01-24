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
					if 'ifpd_query_set' == cmd[0]:
						outdir_id = 4
					elif 'ifpd_query_probe' == cmd[0]:
						outdir_id = 3

					query_id = os.path.basename(cmd[outdir_id])

					config = configparser.ConfigParser()
					with open(f'{cmd[outdir_id]}.config', 'r') as IH:
						config.read_string("".join(IH.readlines()))

					logging.debug(f'Running query "{query_id}"')
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()
					config['GENERAL']['status'] = 'running'
					config['WHEN']['start_time'] = f'{timestamp}'
					config['WHEN']['start_isotime'] = isotimestamp
					with open(f'{cmd[outdir_id]}.config', 'w+') as OH:
						config.write(OH)
					sp.call(cmd)
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()

					logging.debug(f'Finished query "{query_id}"')
					config['GENERAL']['status'] = 'done'
					config['WHEN']['done_time'] = f'{timestamp}'
					config['WHEN']['done_isotime'] = isotimestamp
					with open(f'{cmd[outdir_id]}.config', 'w+') as OH:
						config.write(OH)
					cmd = self.queue.task_done(cmd)

		return

# END ==========================================================================

################################################################################
