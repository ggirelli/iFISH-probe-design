#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Probe-design Query manager
# 
# TODO:
# 	- Split Query.get_data in smaller functions.
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import numpy as np
import os
import pandas as pd

# CLASSES ======================================================================

class Query:
	'''Single query class.'''

	def get_next_id(query_path, queue):
		'''Identify next query ID.

		Args:
			query_path (string): path to the query folder.
			queue (Queue): a Queue object.

		Returns:
			(string): the next query id.
		'''

		# Existing queries
		qe = [int(x) for x in next(os.walk(query_path))[1]]

		# Queued queries
		qe.extend([int(task[1]) for task in queue.queue])

		# Find next_id (fill gaps)
		next_id = 0
		while next_id in qe:
			next_id += 1

		# Output
		return(str(next_id))

	def get_data(query_id, query_path):
		'''Retrieve query data.

		Args:
			query_id (string): query folder name.
			query_path (string): path to the query folder.

		Returns:
			Dictionary containing query data.
		'''

		# Empty dictionary for output
		d = {'query_id' : query_id}

		# Check that the query exists
		dpath = query_path + query_id + '/'
		if not os.path.isdir(dpath):
			return(d)

		# Check DONE status
		d['done'] = False
		d['error'] = ''
		if os.path.exists(dpath + 'DONE'):
			d['done'] = True
		else:
			if os.path.exists(dpath + 'ERROR'):
				f = open(dpath + 'ERROR', 'r')
				d['error'] = ''.join(f.readlines())
				f.close()

		# Read configuration
		d['data'] = {}
		d['nodata'] = False
		if os.path.exists(dpath + 'config.tsv'):
			f = open(dpath + 'config.tsv', 'r')
			for row in f.readlines():
				row = row.strip('\r\n').split('\t')
				d['data'][row[0]] = row[1]
			f.close()
		else:
			d['nodata'] = True

		# Read cmd
		if os.path.exists(dpath + 'cmd'):
			f = open(dpath + 'cmd', 'r')
			d['cmd'] = ''.join(f.readlines())
			f.close()
		else:
			d['cmd'] = 'No command line found.'

		# Read log
		if os.path.exists(dpath + 'log'):
			f = open(dpath + 'log', 'r')
			d['log'] = ''.join(f.readlines())
			f.close()
		else:
			d['log'] = 'No log found'

		# Read candidate table
		if os.path.exists(dpath + 'probes.tsv'):
			d['candidates'] = pd.read_csv(dpath + 'probes.tsv', sep = '\t')
			d['candidates'] = np.array(d['candidates']).tolist()
		elif os.path.exists(dpath + 'sets.tsv'):
			d['candidates'] = pd.read_csv(dpath + 'sets.tsv', sep = '\t')
			d['candidates'] = np.array(d['candidates']).tolist()
		else:
			d['candidates'] = np.array([])

		# Output
		return(d)

# END ==========================================================================

################################################################################
