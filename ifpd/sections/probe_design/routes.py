#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Probe-design Route manager
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import bottle as bot
import configparser
import hashlib
import os
import shlex
import time

import ifpd as fp
from ifpd.sections import routes
from ifpd.sections.probe_design.query import Query

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

		dname = ('<dname:re:(images|documents)>',)
		route = '/q/<query_id>/c/<candidate_id>/%s/<path>' % dname
		self.add_route('candidate_static_file', 'route', route)

		dname = ('<dname:re:(images|documents)>',)
		route = '/q/<query_id>/cs/<candidate_id>/%s/<path>' % dname
		self.add_route('candidate_set_static_file', 'route', route)

		route = '/q/<query_id>/c/<candidate_id>/documents/<path:re:.*>/download/'
		self.add_route('candidate_static_file_download', 'route', route)

		route = '/q/<query_id>/cs/<candidate_id>/documents/<path:re:.*>/download/'
		self.add_route('candidate_set_static_file_download', 'route', route)

		route = '/q/<query_id>/download/'
		self.add_route('query_download', 'route', route)

		route = '/q/<query_id>/c/<candidate_id>/download/'
		self.add_route('candidate_download', 'route', route)

		route = '/q/<query_id>/cs/<candidate_id>/download/'
		self.add_route('candidate_set_download', 'route', route)

		# Pages ----------------------------------------------------------------

		self.add_route('home', 'route', '/')
		self.add_route('home', 'view', 'home.tpl')

		self.add_route('query', 'route', '/q/<query_id>')
		self.add_route('query', 'view', 'query.tpl')

		uri = '/q/<query_id>/c/<candidate_id>'
		self.add_route('candidate_probe', 'route', uri)
		self.add_route('candidate_probe', 'view', 'candidate_probe.tpl')

		uri = '/q/<query_id>/cs/<candidate_id>'
		self.add_route('candidate_probe_set', 'route', uri)
		self.add_route('candidate_probe_set', 'view', 'candidate_probe_set.tpl')

		# Forms ----------------------------------------------------------------

		self.add_route('single_query', 'post', '/single_query')

		self.add_route('multi_query', 'post', '/multi_query')

		self.add_route('single_queries', 'post', '/single_queries')

		# Errors ---------------------------------------------------------------

		self.add_route('error404', 'error', 404)
		self.add_route('error500', 'error', 500)

		return

	# Static files -------------------------------------------------------------

	def candidate_static_file(routes, self,
		query_id, candidate_id, dname, path):
		'''Access candidate static files.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
			dname (string): file type.
			path (string): file name.
		'''
		ipath = '%s/query/%s/candidates/probe_%s/' % (
			self.static_path, query_id, candidate_id)
		return(bot.static_file(path, ipath))

	def candidate_set_static_file(routes, self,
		query_id, candidate_id, dname, path):
		'''Access candidate static files.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
			dname (string): file type.
			path (string): file name.
		'''
		ipath = '%s/query/%s/candidates/set_%s/' % (
			self.static_path, query_id, candidate_id)
		return(bot.static_file(path, ipath))

	def candidate_static_file_download(routes, self,
		query_id, candidate_id, path):
		'''Download candidate static files.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
			dname (string): file type.
			path (string): file name.
		'''
		ipath = '%s/query/%s/candidates/probe_%s/' % (
			self.static_path, query_id, candidate_id)
		outname = 'q_%s.%s' % (query_id, path)
		return(bot.static_file(path, ipath, download = outname))

	def candidate_set_static_file_download(routes, self,
		query_id, candidate_id, path):
		'''Download candidate static files.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
			dname (string): file type.
			path (string): file name.
		'''
		ipath = '%s/query/%s/candidates/set_%s/' % (
			self.static_path, query_id, candidate_id)
		outname = 'q_%s.%s' % (query_id, path)
		return(bot.static_file(path, ipath, download = outname))

	def query_download(routes, self,
		query_id):
		'''Download compressed query output.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
		'''
		ipath = '%s/query/%s/' % (self.static_path, query_id)
		path = '%s.zip' % query_id
		outname = 'q_%s' % path
		return(bot.static_file(path, ipath, download = outname))

	def candidate_download(routes, self,
		query_id, candidate_id):
		'''Download compressed candidate output.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
		'''
		ipath = '%s/query/%s/candidates/' % (self.static_path, query_id)
		path = 'probe_%s.zip' % candidate_id
		outname = 'q_%s.%s' % (query_id, path)
		return bot.static_file(path, ipath, download = outname)

	def candidate_set_download(routes, self,
		query_id, candidate_id):
		'''Download compressed candidate output.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
		'''
		ipath = '%s/query/%s/candidates/' % (self.static_path, query_id)
		path = 'set_%s.zip' % (candidate_id)
		outname = 'q_%s.%s' % (query_id, path)
		return bot.static_file(path, ipath, download = outname)

	# Pages --------------------------------------------------------------------

	def home(routes, self):
		'''Home-page.

		Args:
			self (App): ProbeDesigner.App instance.
		'''

		d = self.vd

		d['title'] = self.tprefix + 'Home'
		d['custom_stylesheets'] = ['home.css', 'style.css']
		d['custom_root_stylesheets'] = []

		
		configPathList = [os.path.join(self.static_path, 'db', p, '.config')
			for p in next(os.walk(os.path.join(self.static_path, 'db')))[1]]
		configPathList.sort()
		d['dbdata'] = []
		for configPath in configPathList:
			with open(configPath, 'r') as IH:
				parser = configparser.ConfigParser()
				parser.read_string("".join(IH.readlines()))
				d['dbdata'].append(parser)
		d['dblist'] = {}
		for p in d['dbdata']:
			dbDir = os.path.basename(p['SOURCE']['outdirectory'])
			dbName = p['DATABASE']['name']
			d['dblist'][dbName] = dbDir
		
		d['qlist'] = []
		qlist = [i for i in next(os.walk(self.qpath))[1]]
		qlist.sort()
		for qid in qlist:
			d['qlist'].append(Query.get_data(str(qid), self.qpath))
		
		return(d)

	def query(routes, self, query_id):
		'''Query output page.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
		'''

		# Template dictionary
		d = self.vd

		# Page title and description
		d['title'] = '%s Query: %s' % (self.tprefix, query_id)

		# Local stylesheets
		d['custom_stylesheets'] = ['query.css', 'style.css']

		# Root stylesheets
		d['custom_root_stylesheets'] = []

		# Query data (query folder)
		d['query'] = Query.get_data(query_id, self.qpath)

		return(d)

	def candidate_probe(routes, self, query_id, candidate_id):
		'''Candidate output page.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
		'''

		# Template dictionary
		d = self.vd

		# Page title and description
		d['title'] = '%s Query: %s' % (self.tprefix, query_id)

		# Local stylesheets
		d['custom_stylesheets'] = ['query.css', 'style.css']

		# Root stylesheets
		d['custom_root_stylesheets'] = []

		# Query data (query folder)
		d['query'] = Query.get_data(query_id, self.qpath)

		# Candidate data
		d['candidate'] = {'id' : candidate_id}

		return(d)

	def candidate_probe_set(routes, self, query_id, candidate_id):
		'''Candidate output page.

		Args:
			self (App): ProbeDesigner.App instance.
			query_id (string): query folder name.
			candidate_id (string): candidate folder name.
		'''

		# Template dictionary
		d = self.vd

		# Page title and description
		d['title'] = '%s Query: %s' % (self.tprefix, query_id)

		# Local stylesheets
		d['custom_stylesheets'] = ['query.css', 'style.css']

		# Root stylesheets
		d['custom_root_stylesheets'] = []

		# Query data (query folder)
		d['query'] = Query.get_data(query_id, self.qpath)

		# Candidate data
		d['candidate'] = {'id' : candidate_id}

		return(d)

	# Form reception -----------------------------------------------------------

	def single_query(routes, self):
		'''Single probe query form reception route.

		Args:
			self (App): ProbeDesigner.App instance.
		'''

		formData = bot.request.forms
		queriedRegion = f'{formData.chromosome}:{formData.start},{formData.end}'
		query_id = f'{queriedRegion}:{time.time()}'
		encoder = hashlib.sha256()
		encoder.update(bytes(query_id, "utf-8"))
		query_id = encoder.hexdigest()

		dbPath = f'{self.static_path}/db/{formData.database}'
		oligoDB = fp.query.OligoDatabase(dbPath, hasNetwork = False)
		min_dist = oligoDB.get_oligo_min_dist()

		cmd = ['ifpd_query_probe']
		cmd.extend([shlex.quote(queriedRegion), shlex.quote(dbPath)])
		cmd.extend([shlex.quote(f'{self.static_path}/query/{query_id}')])
		cmd.extend(['--order', shlex.quote(formData.f1),
			shlex.quote(formData.f2), shlex.quote(formData.f3)])
		cmd.extend(['--filter-thr', shlex.quote(formData.f1_threshold)])
		cmd.extend(['--n-oligo', shlex.quote(formData.n_oligo)])
		cmd.extend(['--max-probes', shlex.quote(formData.max_probes)])
		cmd.extend(['--min-dist', shlex.quote(min_dist)])

		parser = configparser.ConfigParser()
		config['GENERAL'] = {
			'name' : formData.name,
			'description' : formData.description
		}
		config['WHERE'] = {
			'db' : formData.database,
			'region' : queriedRegion
		}
		config['WHAT'] = {
			'n_oligo' : formData.n_oligo,
			'threshold' : formData.f1_threshold,
			'max_probes' : formData.max_probes
		}
		config['HOW'] = {
			'f1' : formData.f1,
			'f2' : formData.f2,
			'f3' : formData.f3
		}
		configPath = os.path.join(self.static_path, 'query',
			f'{query_id}.config')
		with open(configPath, 'w+') as OH:
			config.write(OH)

		# Add query to the queue
		self.queue.put(cmd)

		# Redirect
		bot.response.status = 303
		bot.response.set_header('Location',
			"%s%s" % (self.root_uri, self.app_uri))

		# Output
		return('Query received.')

	def multi_query(routes, self):
		'''Multi probe query form reception route.

		Args:
			self (App): ProbeDesigner.App instance.
		'''

		fdata = bot.request.forms

		# Build query command line
		cmd = ['fprode_dbquery']
		cmd.extend([Query.get_next_id(self.qpath, self.queue)])
		cmd.extend([shlex.quote(fdata.multi_name)])
		cmd.extend([shlex.quote(fdata.multi_chromosome)])
		cmd.extend([shlex.quote(fdata.multi_start)])
		cmd.extend([shlex.quote(fdata.multi_end)])
		dbpath = '%s/db/%s' % (self.static_path, fdata.multi_database)
		cmd.extend([shlex.quote(dbpath)])
		cmd.extend(['--n_oligo', shlex.quote(fdata.multi_n_oligo)])
		cmd.extend(['--f1_thr', shlex.quote(fdata.multi_f1_threshold)])
		cmd.extend(['--n_probes', shlex.quote(fdata.multi_n_probes)])
		cmd.extend(['--win_shift', shlex.quote(fdata.multi_win_shift)])
		feat_order = []
		feat_order.append(fdata.f1)
		feat_order.append(fdata.f2)
		feat_order.append(fdata.f3)
		cmd.extend(['--feat_order', shlex.quote(','.join(feat_order))])
		cmd.extend(['--outdir', '%s/query/' % self.static_path])
		cmd.extend(['--description', shlex.quote(fdata.multi_description)])

		# Add query to the queue
		self.queue.put(cmd)

		# Redirect
		bot.response.status = 303
		bot.response.set_header('Location',
			"%s%s" % (self.root_uri, self.app_uri))

		# Output
		return('Query received.')

	def single_queries(routes, self):
		'''Single probe queries reception route.

		Args:
			self (App): ProbeDesigner.App instance.
		'''

		# Read uploaded file
		data = bot.request.files.data
		raw = [row.decode('utf-8') for row in data.file.readlines()]

		# Submit query
		for row in raw:
			args = row.strip().split('\t')

			# Build query command line
			cmd = ['fprode_dbquery']
			cmd.extend([Query.get_next_id(self.qpath, self.queue)])
			cmd.extend([shlex.quote(args[0])])
			cmd.extend([shlex.quote(e) for e in args[3:6]])
			cmd.extend([shlex.quote('%s/db/%s' % (self.static_path, args[2]))])
			cmd.extend(['--n_oligo', shlex.quote(args[6])])
			cmd.extend(['--f1_thr', shlex.quote(args[7])])
			cmd.extend(['--max_probes', shlex.quote(args[8])])
			cmd.extend(['--feat_order', shlex.quote(args[9])])
			cmd.extend(['--outdir', '%s/query/' % self.static_path])
			cmd.extend(['--description', shlex.quote(args[1])])

			# Add query to the queue
			self.queue.put(cmd)

		# Redirect
		bot.response.status = 303
		bot.response.set_header('Location',
			"%s%s" % (self.root_uri, self.app_uri))

		# Output
		return('Query received.')

	# Error --------------------------------------------------------------------

# END ==========================================================================

################################################################################
