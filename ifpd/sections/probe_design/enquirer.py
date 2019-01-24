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

import logging
import os
import subprocess as sp
import threading

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

					logging.debug(f'Running query "{query_id}"')
					sp.call(cmd)

					logging.debug(f'Finished query "{query_id}"')
					cmd = self.queue.task_done(cmd)

		return

# END ==========================================================================

################################################################################
