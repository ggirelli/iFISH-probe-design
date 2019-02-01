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

	def readQueryConfig(self, queryDir):
		config = configparser.ConfigParser()
		with open(f'{queryDir}.config', 'r') as IH:
			config.read_string("".join(IH.readlines()))
		return config

	def writeQueryConfig(self, queryDir, config):
		with open(f'{queryDir}.config', 'w+') as OH:
			config.write(OH)

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
					EH = open(f"{cmd[outdir_id]}.error.log", "w+")



					logging.debug(f'Running query "{query_id}"')
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()
					config = self.readQueryConfig(cmd[outdir_id])
					config['GENERAL']['status'] = 'running'
					config['WHEN']['start_time'] = f'{timestamp}'
					config['WHEN']['start_isotime'] = isotimestamp
					self.writeQueryConfig(cmd[outdir_id], config)

					sp.call(cmd, stderr = EH)
					timestamp = time.time()
					isotimestamp = datetime.datetime.fromtimestamp(
						timestamp).isoformat()
					logging.debug(f'Finished query "{query_id}"')
					config = self.readQueryConfig(cmd[outdir_id])
					config['GENERAL']['status'] = 'done'
					config['WHEN']['done_time'] = f'{timestamp}'
					config['WHEN']['done_isotime'] = isotimestamp
					self.writeQueryConfig(cmd[outdir_id], config)
					cmd = self.queue.task_done(cmd)
					EH.close()

		return

# END ==========================================================================

################################################################################
