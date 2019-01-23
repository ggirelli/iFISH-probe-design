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

				# Retreive query settings
				cmd = self.queue.get()

				print(cmd)

				# If the queue released a task
				if not type(None) == type(cmd):

					# Start query
					msg = 'Running query #%s' % str(cmd[1])
					logging.debug(msg)

					# Run query
					sp.call(cmd)

					# Finish query
					msg = 'Finished query #%s' % str(cmd[1])
					logging.debug(msg)
					cmd = self.queue.task_done(cmd)

		# Close
		return

# END ==========================================================================

################################################################################
