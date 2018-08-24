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
		dpath = '%s%s/' % (query_path, query_id)
		if not os.path.isdir(dpath):
			return(d)

		# Check DONE status
		d['done'] = False
		d['error'] = ''
		if os.path.exists('%sDONE' % dpath):
			d['done'] = True
		else:
			if os.path.exists('%sERROR' % dpath):
				f = open('%sERROR' % dpath, 'r')
				d['error'] = ''.join(f.readlines())
				f.close()

		# Read configuration
		d['data'] = {}
		d['nodata'] = False
		if os.path.exists('%sconfig.tsv' % dpath):
			f = open('%sconfig.tsv' % dpath, 'r')
			for row in f.readlines():
				row = row.strip('\r\n').split('\t')
				d['data'][row[0]] = row[1]
			f.close()
		else:
			d['nodata'] = True

		# Read cmd
		if os.path.exists('%scmd' % dpath):
			f = open('%scmd' % dpath, 'r')
			d['cmd'] = ''.join(f.readlines())
			f.close()
		else:
			d['cmd'] = 'No command line found.'

		# Read log
		if os.path.exists('%slog' % dpath):
			f = open('%slog' % dpath, 'r')
			d['log'] = ''.join(f.readlines())
			f.close()
		else:
			d['log'] = 'No log found'

		# Read candidate table
		if os.path.exists('%sprobes.tsv' % dpath):
			d['candidates'] = pd.read_csv('%sprobes.tsv' % dpath, sep = '\t')
			d['candidates'] = np.array(d['candidates']).tolist()
		elif os.path.exists('%ssets.tsv' % dpath):
			d['candidates'] = pd.read_csv('%ssets.tsv' % dpath, sep = '\t')
			d['candidates'] = np.array(d['candidates']).tolist()
		else:
			d['candidates'] = np.array([])

		# Output
		return(d)

# END ==========================================================================

################################################################################
