#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Date: 161121
# Description: Design single FISH probe using extracted database data.
# Notes: oligomer length k identified from the database string,
# 		 which is supposed to contain the '_runKmer_' bit.
# 
# Todo:
# 	In multi probe design, make probe_set as a dictionary.
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import argparse
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import pandas as pd
from scipy import stats
import shutil
import sys
import urllib2
import xml.etree.ElementTree
import zipfile

# INPUT ========================================================================

# Add script description
parser = argparse.ArgumentParser(
	description = 'Query database for a FISH probe.'
)

# Add params
parser.add_argument('id', type = str, nargs = 1,
	help = 'Query ID.')
parser.add_argument('name', type = str, nargs = 1,
	help = 'Query name.')
parser.add_argument('chrom', metavar = 'chr', type = str, nargs = 1,
	help = 'Chromosome in "ChrXX" format.')
parser.add_argument('start', metavar = 'start', type = int, nargs = 1,
	help = 'Probe range starting position.')
parser.add_argument('end', metavar = 'end', type = int, nargs = 1,
	help = 'Probe range ending position.')
parser.add_argument('db', metavar = 'db', type = str, nargs = 1,
	help = 'Database folder path.')
parser.add_argument('--description', metavar = 'descr', type = str, nargs = 1,
	default = [''], help = 'Query description')
parser.add_argument('--feat_order', metavar = 'fo', type = str, nargs = 1,
	default = ['size,spread,centrality'], help = 'Comma-separated features.')
parser.add_argument('--f1_thr', metavar = 'ft', type = float, nargs = 1,
	default = [1.1], help = 'Threshold of first feature filter, '
	+ 'used to identify a range around the best value. '
	+ 'It\'s the percentage range around it. Accepts values from 0 to 1.')
parser.add_argument('--min_d', metavar = 'md', type = int, nargs = 1,
	default = [10], help = 'Minimum distance between consecutive oligos.')
parser.add_argument('--n_oligo', metavar = 'no', type = int, nargs = 1,
	default = [48], help = 'Number of oligos per probe.')
parser.add_argument('--n_probes', metavar = 'np', type = int, nargs = 1,
	default = [1], help = 'Number of probes to design.')
parser.add_argument('--max_probes', metavar = 'mp', type = int, nargs = 1,
	default = [-1], help = 'Maximum number of output probe candidates.'
	+ ' Set to "-1" to retrieve all candidates.')
parser.add_argument('--win_shift', metavar = 'ws', type = float, nargs = 1,
	default = [.1], help = 'Window size fraction for shifting the windows.')
parser.add_argument('--outdir', metavar = 'od', type = str, nargs = 1,
	default = ['query'], help = 'Query output directory.')
parser.add_argument('-f', type = bool, nargs = '?', const = [True],
	default = [False], help = 'Force overwriting of the query if already run.')

# Parse arguments
args = parser.parse_args()

# general
query_id = args.id[0]
name = args.name[0]
description = args.description[0]

# output
outdir = args.outdir[0]
max_probes = args.max_probes[0]
force_mode = args.f[0]

# where
chrom = args.chrom[0]
start = args.start[0]
end = args.end[0]

# what
n_probes = args.n_probes[0]
n_oligo = args.n_oligo[0]

# Minimum distance between consecutive oligos
min_d = args.min_d[0]

# Threshold for first feature selection
f1_thr = args.f1_thr[0]

# Extracted database folder
dbpath = args.db[0]

# Features order
feats = ['size', 'centrality', 'spread']
feats_order = args.feat_order[0].split(',')
feats_order = [feats.index(feats_order[i]) for i in range(len(feats_order))]

# Extract k information from database selection
k = dbpath.split('/')[-1].split('_')
k = int(''.join([i for i in k if 'kmer' in i]).strip('kmer'))

# Shift window size fraction
win_shift = max(0.0, min(1.0, args.win_shift[0]))

# FUNCTIONS ====================================================================

def add_trailing_slash(path, slash = None):
	'''Add trailing slash to a path.

	Args:
		path (string): path.
		slash (string): trailing slash, defaults to '/'.
	'''

	# Set default slash
	if type(None) == type(slash):
		slash = '/'

	# Add trailing slash if needed
	if slash != path[-1]:
		path += slash

	# Output
	return(path)

def log(msg, lpath, v = None):
	'''Log.

	Args:
		msg (string): message to be logged.
		lpath (string): log path.
		v (bool): verbosity. Default True, optional.
	'''

	# Set verbosity default
	if type(None) == type(v):
		v = True

	# Log message
	f = open(lpath, 'a+')
	f.write(add_trailing_slash(msg, slash = '\n'))
	f.close()

	if v:
		# Print message
		print(msg)

def done(dirpath):
	'''Create DONE file.

	Args:
		dirpath (string): directory path.
	'''

	f = open(add_trailing_slash(dirpath) + 'DONE', 'w+')
	f.close()

def zipdir(path, ziph):
	'''Zips a directory. Based on https://goo.gl/GeCPVm.

	Args:
		path (string): directory path.
		ziph (Zipfile): zipfile handler.

	Returns:
		None.
	'''

	# Check that the folder exists
	if not os.path.isdir(path):
		return()

	# Iterate
	for root, dirs, files in os.walk(path):
		for file in files:
			ziph.write(os.path.join(root, file))

def calc_density(data, **kwargs):
	"""
	Calculate the Gaussian KDE of the provided data series.
	
	Args:
		sigma (float): standard deviation used for covariance calculation (opt).
		nbins (int): #steps for the density curve calculation (opt, def: 1000).

	Returns:
		dict: density curve (x, y) and function (f).
	"""

	# Default values
	if not 'sigma' in kwargs.keys():
		sigma = .2
	else:
		sigma = kwargs['sigma']

	if not 'nbins' in kwargs.keys():
		nbins = 1000
	else:
		nbins = kwargs['nbins']

	# If only one nucleus was found
	if 1 == len(data):
		f = eval('lambda x: 1 if x == ' + str(data[0]) + ' else 0')
		f = np.vectorize(f)
		return({
			'x' : np.array([data[0]]),
			'y' : np.array([1]),
			'f' : f
		})

	# Prepare density function
	density = stats.gaussian_kde(data)

	# Re-compute covariance
	density.covariance_factor = lambda : sigma
	density._compute_covariance()

	# Output
	out = {}
	out['x'] = np.linspace(min(data), max(data), nbins)
	out['f'] = density
	out['y'] = density(out['x'])
	return(out)

def is_single_probe(n_probes):
	'''Check the number of probes to be designed.

	Args:
		n_probes (int): number of requested probes.
	'''
	return(1 == n_probes)

def get_min_size(n_oligo, k, d, n_probes = None):
	'''Calculate the minimum window size to get the number of requested oligos.

	Args:
		n_oligo (int): number of requested oligos.
		k (int): oligo size [nt].
		d (int): minimum distance between consecutive oligos [nt].
		n_probes (int): number of probes, defaults to 1.

	Returns:
		Minimum window size.
	'''

	if type(n_probes) is type(None):
		# Single probe window
		return(k * n_oligo + d * (n_oligo - 1))
	else:
		# Multiple probe window
		probe_size = k * n_oligo + d * (n_oligo - 1)
		return(probe_size * n_probes + d * (n_probes - 1))

def check_window(start, end, min_size):
	'''Check if the window is large enough.

	Args:
		start (int): window start position.
		end (int): window end position.
		min_size (int): minimum window size.
	'''
	return(end - start >= min_size)

def is_chrom_in_db(dbpath, crhom):
	'''Check if a chromosome is present in a database.

	Args:
		dbpath (string): database folder path.
		chrom (string): chromosome to be extracted.
	'''
	
	# Add trailing slash
	dbpath = add_trailing_slash(dbpath)

	return(os.path.isfile(dbpath + chrom))

def get_chromosome(dbpath, chrom):
	'''Retrieve a chromosome oligos.

	Args:
		dbpath (string): database folder path.
		chrom (string): chromosome to be extracted.

	Returns:
		List of oligo start positions.
	'''

	# Add trailing slash
	dbpath = add_trailing_slash(dbpath)

	# Check if the database has the requested chromosome
	if not is_chrom_in_db(dbpath, chrom):
		return(np.array([]))

	# Read chromosome
	return(np.array(pd.read_csv(dbpath + chrom)))

def subset_db(poss, start, end):
	'''Selects only the positions in the specified window.

	Args:
		poss (nd.array): list of oligo start positions.
		start (int): window start.
		end (int): window end.

	Returns:
		Selected positions.
	'''
	poss = poss[np.where(poss >= start)]
	poss = poss[np.where(poss <= end)]
	return(poss)

def get_probe_candidates(poss, n_oligo):
	'''Groups oligos into candidate probes.

	Args:
		poss (nd.array): list of oligo positions.
		n_oligo (int): number of oligos per probe.

	Returns:
		List of probe candidates.
	'''

	# Empty list for grouped oligos
	groups = []

	# Prepare groups
	for i in range(0, poss.shape[0] - n_oligo + 1):
		groups.append(poss[i:(i + n_oligo)])

	# Output
	return(groups)

def calc_probe_size(probe, k, **kwargs):
	'''Calculates the size of a probe.

	Args:
		probe(nd.array): list of probe oligo positions.
		k (int): oligo size [nt].
	'''
	return(probe[-1] - probe[0] + k)

def calc_probe_centrality(probe, k, start, end, **kwargs):
	'''Calculates the probe centrality.

	Args:
		probe(nd.array): list of probe oligo positions.
		k (int): oligo size [nt].
		start (int): window start position.
		end (int): window end position.

	Returns:
		0 when on the window's border.
		1 when perfectly central.
	'''

	# Calculate probe half-size and center
	phsize = calc_probe_size(probe, k) / 2.0
	pcenter = probe[0] + phsize

	# Calculate window half-size and center
	whsize = (end - start) / 2.0
	wcenter = start + whsize

	# Output
	return((whsize - abs(wcenter - pcenter)) / whsize)

def calc_probe_spread(probe, k, **kwargs):
	'''Calculates the probe spread.

	Args:
		probe(nd.array): list of probe oligo positions.
		k (int): oligo size [nt].

	Returns:
		Smaller when dishomogeneous, larger when homogeneous.
	'''
	return(1 / np.std(np.diff(probe) + k))

def calc_multi_probe_spread(starts, ends, **kwargs):
	'''
	'''

	d = abs(ends[:-1] - starts[1:])
	s = ends - starts
	m =	np.std(d)/np.mean(d) + np.std(s)/np.mean(ends - starts)
	m /= 2.0
	m = 1.0 / float(m)
	return(m)

def calc_feature(fid, ff = None, **kwargs):
	'''Calculate the specified feature.

	Args:
		fid (string): key for the requested feature.
		ff (dict): dictionary with feature:function couples. (optional)
		kwargs (dict): parameters for the feature function
	'''

	# Setup default feature functions
	if type(None) == type(ff):
		ff = {}
		ff['size'] = calc_probe_size
		ff['centrality'] = calc_probe_centrality
		ff['spread'] = calc_probe_spread

	# Calculate feature
	return(ff[fid](**kwargs))

def get_best_feature(vs, fid, ff = None):
	'''Get best value the specified feature.

	Args:
		vs (list): list of feature values.
		fid (string): key for the requested feature.
		ff (dict): dictionary with feature:function couples. (optional)
	'''

	# Setup default feature functions
	if type(None) == type(ff):
		ff = {}
		ff['size'] = lambda (x): min(x)
		ff['centrality'] = lambda (x): max(x)
		ff['spread'] = lambda (x): max(x)

	# Calculate best
	return(ff[fid](vs))

def select_range_high(fs, thr):
	'''Select feature values based on a threshold lower than the best.

	Args:
		fs (list): list of feature values.
		thr (float): threshold value (0 < thr < 1).

	Returns:
		Indices of selected values.
	'''

	# Fix thr value
	if thr > 1:
		thr = 1
	if thr < 0:
		thr = 0

	# Identify best feature value
	best = max(fs)

	# Calulate threshold border
	border = best - (best * thr)

	# Return selected values
	return(np.where(np.array(fs) >= border)[0])

def select_range_low(fs, thr):
	'''Select feature values based on a threshold higher than the best.

	Args:
		fs (list): list of feature values.
		thr (float): threshold value (0 < thr < 1).

	Returns:
		Indices of selected values.
	'''

	# Fix thr value
	if thr > 1:
		thr = 1
	if thr < 0:
		thr = 0

	# Identify best feature
	best = min(fs)

	# Calulate threshold border
	border = best + (best * thr)

	# Return selected values
	return(np.where(fs <= border)[0])

def select_range_feature(vs, thr, fid, ff = None):
	'''Get best value the specified feature.

	Args:
		vs (list): list of feature values.
		thr (float): threshold value.
		fid (string): key for the requested feature.
		ff (dict): dictionary with feature:function couples. (optional)
	'''

	# Setup default feature functions
	if type(None) == type(ff):
		ff = {}
		ff['size'] = select_range_low
		ff['centrality'] = select_range_high
		ff['spread'] = select_range_high

	# Calculate best
	return(ff[fid](vs, thr))

def rank_feature(vs, fid, ff = None):
	'''Rank feature values.

	Args:
		vs (list): list of feature values.
		fid (string): key for the requested feature.
		ff (dict): dictionary with feature:function couples. (optional)
	'''

	# Setup default feature functions
	if type(None) == type(ff):
		ff = {}
		ff['size'] = lambda (x): np.argsort(vs)
		ff['centrality'] = lambda (x): np.argsort(vs)[::-1]
		ff['spread'] = lambda (x): np.argsort(vs)[::-1]

	# Calculate best
	return(ff[fid](vs))	

def get_seq(chrom, start, stop, genome = None):
	'''Retrieve genomic sequence.

	Args:
		chrom (string): chromosome in the format chrXX.
		start (int): start position.
		stop (int): end position.
		genome (string): genome (e.g., hg19).

	Returns:
		Sequence from UCSC.
	'''

	# Set default genome
	if type(None) == type(genome):
		genome = 'hg19'

	# Contact UCSC
	data = (genome, chrom, start, stop)
	uri = 'http://genome.ucsc.edu/cgi-bin/das/%s/dna?segment=%s:%d,%d' % data
	file = urllib2.urlopen(uri)
	data = file.read()
	file.close()

	# Extract sequence
	seq = xml.etree.ElementTree.fromstring(data)[0][0].text
	seq = seq.replace('\n', '').replace('\r', '').replace(' ', '')

	# Output
	return(seq)

def plot_window(chrom, start, stop, probe, k, path):
	'''Plot probe.

	Args:
		chrom (string): chromosome.
		start (int): window start.
		stop (int): window stop.
		probe (list): list of oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure()

	# Plot genome
	wsize = stop - start
	plt.plot([start, stop], [0, 0], 'k', linewidth = 4.0, label = 'Genome')
	plt.hold(True)
	plt.plot([start + wsize/2., start + wsize/2.], [-1, 1], 'r--',
		label = 'Window center')

	# Plot probe
	psize = max(probe) - min(probe) + k
	plt.plot([min(probe), max(probe) + k], [0, 0], 'c-', linewidth = 4.0,
		label = 'Probe')
	plt.plot([min(probe) + psize/2., min(probe) + psize/2.], [-1, 1], 'c--',
		label = 'Probe center')

	# Hide Y axis
	plt.gca().axes.get_yaxis().set_visible(False)

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, start, stop))
	plt.xlabel('genomic coordinate [nt]')

    # Add legend
	plt.legend(fontsize = 'small', loc = 'best')

	# Export
	plt.savefig('%swindow.png' % path, format = 'png', bbox_inches='tight')

	# Close
	plt.close(fig)

def plot_probe(chrom, probe, k, path):
	'''Plot probe.

	Args:
		chrom (string): chromosome.
		probe (list): list of oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure(figsize = (20, 5))

	# Plot genome
	genome, = plt.plot([min(probe), max(probe) + k], [0, 0], 'k',
		linewidth = 4.0, label = 'Genome')
	plt.hold(True)

	# Plot oligos
	for oi in probe:
		oligo, = plt.plot([oi, oi + k], [0, 0], 'c', linewidth = 2.0,
			label = 'Oligo')
		oligo_center, = plt.plot([oi + k/2., oi + k/2.], [-.1, .1], 'c:',
			label = 'Oligo center')

	# Hide Y axis
	plt.gca().axes.get_yaxis().set_visible(False)

	# Set Y axis limits
	plt.ylim((-.5, .5))

	# Set X axis ticks
	start = min(probe)
	stop = max(probe) + k
	step = (stop - start) / 5.
	plt.gca().axes.get_xaxis().set_ticks(range(start, stop, int(step)))

	# Legend
	plt.legend(handles = [genome, oligo, oligo_center],
		fontsize = 'small', loc = 'best')

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, min(probe), max(probe) + k))
	plt.xlabel('genomic coordinate [nt]')

	# Export
	plt.savefig('%sprobe.png' % path, format = 'png', bbox_inches='tight')

	# Close
	plt.close(fig)

def plot_oligo_distr(chrom, probe, k, path):
	'''Plot oligo distribution.

	Args:
		chrom (string): chromosome.
		probe (list): list of oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure()

	# Plot oligos
	plt.plot([0, len(probe) - 1], [min(probe) + k/2., max(probe) + k/2.], 'k-',
		label = 'Homogeneous distribution')
	plt.hold(True)
	plt.plot(range(len(probe)), np.array(probe) + k/2., 'r.',
		label = 'Oligo')

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, min(probe), max(probe) + k))
	plt.xlabel('oligo number')
	plt.ylabel('genomic coordinate [nt]')

	# Add legend
	plt.legend(fontsize = 'small', loc = 'best')

	# Export
	plt.savefig('%soligo.png' % path, format = 'png')

	# Close
	plt.close(fig)

def plot_probe_distr(chrom, probe_set, k, path):
	'''Plot probe distribution.

	Args:
		chrom (string): chromosome.
		probe_set (list): list of probe oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure()

	# Retrieve oligo positions
	oligos = []
	[oligos.extend(probe_set[i].tolist()) for i in range(len(probe_set))]

	# Retrieve probe positions
	psta = np.array([min(probe_set[i]) for i in range(len(probe_set))])
	psto = np.array([max(probe_set[i]) for i in range(len(probe_set))])
	pcen = (psto - psta) / 2. + psta

	# Plot probes
	plt.plot([0, len(psta) - 1], [min(pcen), max(pcen)], 'k-',
		label = 'Homogeneous distribution')
	plt.hold(True)
	plt.plot(range(len(pcen)), np.array(pcen), 'r.', label = 'Probe')

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, min(pcen), max(pcen) + k))
	plt.xlabel('probe number')
	plt.ylabel('genomic coordinate [nt]')

	# Set limits
	plt.xlim((-1, len(psta)))

	# Add legend
	plt.legend(fontsize = 'small', loc = 'best')

	# Export
	plt.savefig('%sdistr.png' % path, format = 'png')

	# Close
	plt.close(fig)

def plot_oligo_distance(chrom, probe, k, path):
	'''Plot oligo distance distribution.

	Args:
		chrom (string): chromosome.
		probe (list): list of oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure()

	# Plot histogram
	diffs = np.diff(np.array(probe)) - k
	plt.hist(diffs, normed = 1, facecolor = 'green', alpha = .5)
	plt.hold(True)

	# Plot density
	density = calc_density(diffs, alpha = .5)
	plt.plot(density['x'].tolist(), density['y'].tolist(), 'b--',
		label = 'Density distribution')

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, min(probe), max(probe) + k))
	plt.xlabel('Distance between consecutive oligos [nt]')
	plt.ylabel('Density')

	# Add legend
	plt.legend(fontsize = 'small', loc = 'best')

	# Export
	plt.savefig('%sdistance.png' % path, format = 'png')

	# Close
	plt.close(fig)

def plot_probe_distance(chrom, probe_set, k, path):
	'''Plot probe distance distribution.

	Args:
		chrom (string): chromosome.
		probe_set (list): list of probe oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure()

	# Retrieve oligo positions
	oligos = []
	[oligos.extend(probe_set[i].tolist()) for i in range(len(probe_set))]

	# Retrieve probe positions
	psta = np.array([min(probe_set[i]) for i in range(len(probe_set))])
	psto = np.array([max(probe_set[i]) for i in range(len(probe_set))])
	pcen = (psto - psta) / 2. + psta
	psize = psto - psta

	# Plot histogram
	diffs = np.diff(np.array(psta)) - psize[:-1]
	plt.hist(diffs, normed = 1, facecolor = 'green', alpha = .5)
	plt.hold(True)

	# Plot density
	density = calc_density(diffs, alpha = .5)
	plt.plot(density['x'].tolist(), density['y'].tolist(), 'b--',
		label = 'Density distribution')

	# Add labels
	plt.suptitle('%s:%d-%d' % (chrom, min(oligos), max(oligos) + k))
	plt.xlabel('Distance between consecutive probes [nt]')
	plt.ylabel('Density')

	# Add legend
	plt.legend(fontsize = 'small', loc = 'best')

	# Export
	plt.savefig('%sdistance.png' % path, format = 'png')

	# Close
	plt.close(fig)

def plot_probe_set(chrom, start, end, k, probe_set, path):
	'''Plot probe set empty windows.

	Args:
		chrom (string): chromosome.
		probe_set (list): list of probe oligo positions.
		k (int): oligo size in nt.
		path (string): output folder path.
	'''

	# Create figure
	fig = plt.figure(figsize = (20, 5))

	wsize = probe_set['windows'][1] - probe_set['windows'][0]

	# Plot windows
	for wstart in probe_set['windows']:
		plt.axvline(x = wstart, ymin = -1, ymax = 1,
			color = 'k')
		plt.hold(True)
	plt.axvline(x = probe_set['windows'][-1] + wsize,
		ymin = -1, ymax = 1, color = 'k', linestyle = ':')

	# Plot empty windows
	for wi in probe_set['empty_windows']:
		plt.gca().add_patch(
			patches.Rectangle(
				(probe_set['windows'][wi], -1),
				probe_set['windows'][1] - probe_set['windows'][0],
				2,
				color = 'r'
			)
		)

	# Add window number
	for wi in range(len(probe_set['windows'])):
		plt.gca().text(probe_set['windows'][wi] + wsize / 2., .5, wi + 1)

	# Black extremities
	plt.gca().add_patch(
		patches.Rectangle(
			(0, -1),
			probe_set['windows'][0],
			2,
			color = 'k'
		)
	)
	plt.gca().add_patch(
		patches.Rectangle(
			(probe_set['windows'][-1] + wsize, -1),
			end - probe_set['windows'][-1] - wsize,
			2,
			color = 'k'
		)
	)

	# Retrieve oligo positions
	oligos = []
	cand = probe_set['candidates']
	[oligos.extend(cand[i].tolist()) for i in range(len(cand))]

	# Plot genome
	genome, = plt.plot([start, end], [0, 0], 'k',
		linewidth = 4.0, label = 'Genome')
	plt.hold(True)

	# Plot probes
	for probe in probe_set['candidates']:
		pstart = min(probe)
		psize = max(probe) - pstart
		oligo, = plt.plot([min(probe), max(probe) + k], [0, 0], 'c',
			linewidth = 2.0, label = 'Probe')
		oligo_center, = plt.plot([pstart + psize / 2., pstart + psize / 2.],
			[-.1, .1], 'c:', label = 'Probe center', linewidth = 2.0)

	# Hide Y axis
	plt.gca().axes.get_yaxis().set_visible(False)

	# Set Y axis limits
	plt.ylim((-1,1))

	# Add labels
	msg = 'Empty windows are reported in red.'
	data = (chrom, start, end, chrom, min(oligos), max(oligos) + k, msg)
	plt.suptitle('Region: %s:%d-%d & Probe set: %s:%d-%d\n%s' % data)
	plt.xlabel('genomic coordinate [nt]')

	# Export
	plt.savefig('%s/windows.png' % path, format = 'png', bbox_inches='tight')

	# Close
	plt.close(fig)

def run_single_probe(dbpath, outdir, lpath, elpath,
	chrom, start, end, k, n_oligo, min_d, max_probes,
	f1_thr, feats_order, feats = None, verbose = None):
	'''Run single probe query.

	Args:
		dbpath (string): database folder path.
		outdir (string): query output directory path.
		lpath (string):  log path.
		elpath (string): error log path.
		max_probes (int): max number of output probe candidates. Set -1 for all.
		chrom (int): chromosome in ChrXX format.
		start (int): probe range starting position.
		end (int): probe range ending position.
		n_oligo (int): number of oligo per probe.
		min_d (int): minimum distance between consecutive oligos.
		f1_thr (float): threshold of the first feature filter.
		feats (list): feature names.
		feats_order (list<int>): order of features.
		k (int): oligo size in nt.

	Returns:
		candidates (list): probe candidates as oligo start position lists.
		fvs (np.array): candidate features.
		cseq (list): probe candidates oligo sequences, per candidate.
	'''

	if type(None) is type(feats):
		feats = ['size', 'centrality', 'spread']
	if type(None) is type(verbose):
		verbose = True

	# Design single probe ------------------------------------------------------
	if verbose: log('\n* SINGLE PROBE DESIGN *\n', lpath)
	if verbose: log('~ Database: ' + dbpath[:-1] + '\n', lpath)

	# Check window size
	if not check_window(start, end, get_min_size(n_oligo, k, min_d)):
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: too many oligos were requested,'
		msg += ' or the specified window was too small.'
		log(msg, elpath)
		sys.exit()

	# Extract oligo positions
	if verbose: log(' · Extracting oligo positions.', lpath)
	poss = subset_db(get_chromosome(dbpath, chrom), start, end)

	# Exit if no oligos were found
	if 0 == len(poss):
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: no oligos found in %s:%i-%i.' % (chrom, start, end)
		log(msg, elpath)
		sys.exit()

	# Divide sets
	if verbose: log(' · Identifying candidate probes.', lpath)
	candidates = get_probe_candidates(poss, n_oligo)
	n_candidates = len(candidates)
	if verbose: log(' >>> Found ' + str(n_candidates) + ' candidates.', lpath)

	# Exit if no candidate probes were found
	if 0 == n_candidates:
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: no candidate probes found '
		msg += 'in %s:%i-%i.' % (chrom, start, end)
		log(msg, elpath)
		sys.exit()

	# Calculate features
	fvs = np.zeros((len(candidates), len(feats)))

	# Calculate first feature --------------------------------------------------
	f1 = feats[feats_order[0]]
	if verbose: log(' · Calculating first feature [' + f1 + '].', lpath)
	for ci in range(len(candidates)):
		fvs[ci, 0] = calc_feature(f1,
			probe = candidates[ci],
			k = k, start = start, end = end)

	# Select best probe candidates based on first feature
	selected = select_range_feature(fvs[:, 0], f1_thr, f1)
	if verbose:
		msg = ' >>> Best ' + f1 + ': ' + str(get_best_feature(fvs[:,0], f1))
		log(msg, lpath)
		log(' · Selecting candidates with threshold: ' + str(f1_thr), lpath)
		log(' >>> Selected ' + str(len(selected)) + ' candidate probes.', lpath)
	candidates = [candidates[i] for i in selected]
	fvs = fvs[selected, :]

	# Calculate second and third feature ---------------------------------------
	f2 = feats[feats_order[1]]
	f3 = feats[feats_order[2]]
	if verbose:
		msg = ' · Calculating second [%s] and third [%s] features.' % (f2, f3)
		log(msg, lpath)
	for ci in range(len(candidates)):
		fvs[ci, 1] = calc_feature(f2,
			probe = candidates[ci],
			k = k, start = start, end = end)
		fvs[ci, 2] = calc_feature(f3,
			probe = candidates[ci],
			k = k, start = start, end = end)

	# Order and rank
	if verbose: log(' · Ranking selected candidates.', lpath)
	rank = rank_feature(fvs[:, 1], f2)
	fvs = fvs[rank, :]
	candidates = [candidates[i] for i in rank]

	# Check nuber of candidates
	if -1 != max_probes:
		if len(candidates) > max_probes:
			if verbose:
				msg = ' · Selecting top ' + str(max_probes) + ' candidates.'
				log(msg, lpath)
			candidates = candidates[0:max_probes]
			fvs = fvs[0:max_probes, :]

	# Retrieve sequence of the whole window ------------------------------------
	if verbose: log(' · Retrieving oligo sequences.', lpath)

	# Select window borders
	sstart = min([min(c) for c in candidates])
	sstop = max([max(c) for c in candidates]) + k
	
	# Get window sequence
	seq = get_seq(chrom, sstart, sstop)

	# Retrieve oligo sequences
	cseq = []
	for c in candidates:
		cseq.append([seq[(i - sstart):(i - sstart + k)] for i in c])

	# Close --------------------------------------------------------------------
	return((candidates, fvs, cseq))

def output_single_probe(query_id, outdir, lpath, chrom, start, end, k,
	candidates, cseq, feats, feats_order, fvs):
	'''Output single probe data.

	Args:
		query_id (string): query ID.
		outdir (string): query output directory path.
		lpath (string):  log path.
		chrom (int): chromosome in ChrXX format.
		start (int): probe range starting position.
		end (int): probe range ending position.
		k (int): oligo size in nt.
		candidates (list): probe candidates as oligo start position lists.
		cseq (list): probe candidates oligo sequences, per candidate.
		feats (list): feature names.
		feats_order (list<int>): order of features.
		fvs (np.array): candidate features.

	Returns:
		None
	'''

	# Output -------------------------------------------------------------------
	log(' · Preparing output.', lpath)

	# Create candidate folders
	for ci in range(len(candidates)):
		dname = outdir + 'candidates/probe_' + str(ci)
		if not os.path.isdir(dname):
			os.makedirs(dname)

	# Identify features
	f1 = feats[feats_order[0]]
	f2 = feats[feats_order[1]]
	f3 = feats[feats_order[2]]

	# Generate recap table for query -------------------------------------------
	log(' >>> Generating general recap table.', lpath)

	f = open(outdir + 'probes.tsv', 'a+')

	# Table header
	head = 'candidate\tchr\tstart\tend\tn_oligo'
	for i in feats_order:
		head += '\t' + feats[i]
	f.write(head + '\n')

	for ci in range(len(candidates)):
		cc = candidates[ci]

		# Table content
		cdata = [ci, chrom, min(cc), max(cc) + k, len(cc)]
		cdata.extend(fvs[ci,:].tolist())
		f.write('%d\t%s\t%d\t%d\t%d\t%f\t%f\t%f\n' % tuple(cdata))

	f.close()

	# Generate a fasta file per candidate --------------------------------------
	log(' >>> Generating candidates fasta files.', lpath)

	for ci in range(len(candidates)):
		cc = candidates[ci]
		pname = 'probe_' + str(ci)
		dname = outdir + 'candidates/' + pname + '/'
		f = open(dname + pname + '.fa', 'a+')
		
		for oi in range(len(cc)):
			data = (oi + 1, chrom, cc[oi], cc[oi] + k, k)
			head = '> Oligo%d %s:%d-%d %d' % data
			f.write(head)
			f.write('\n' + cseq[ci][oi].upper() + '\n')

		f.close()

	# Generate a bed file per candidate ----------------------------------------
	log(' >>> Generating candidates bed files.', lpath)

	for ci in range(len(candidates)):
		cc = candidates[ci]
		pname = 'probe_' + str(ci)
		dname = outdir + 'candidates/' + pname + '/'
		f = open(dname + pname + '.bed', 'a+')
		
		for oi in range(len(cc)):
			data = (chrom, cc[oi], cc[oi] + k, k)
			head = '%s\t%d\t%d\t%d\n' % data
			f.write(head)

		f.close()

	# Generate config per candidate --------------------------------------------
	log(' >>> Generating candidates config file.', lpath)

	for ci in range(len(candidates)):
		cc = candidates[ci]
		dname = outdir + 'candidates/probe_' + str(ci)

		f = open(dname + '/config', 'a+')
		
		f.write('chr\t%s\n' % (chrom,))
		f.write('start\t%d\n' % (min(cc),))
		f.write('stop\t%d\n' % (max(cc) + k,))
		f.write('k\t%d\n' % (k,))
		f.write('n_oligo\t%d\n' % (len(cc),))
		f.write('%s\t%f\n' % (f1, fvs[ci, 0]))
		f.write('%s\t%f\n' % (f2, fvs[ci, 1]))
		f.write('%s\t%f\n' % (f3, fvs[ci, 2]))

		f.close()

	# Generate plots per candidate ---------------------------------------------
	log(' >>> Plotting candidates.', lpath)

	for ci in range(len(candidates)):
		cc = candidates[ci]
		dname = '%scandidates/probe_%d/' % (outdir, ci)
		plot_window(chrom, start, end, cc, k, dname)
		plot_probe(chrom, cc, k, dname)
		plot_oligo_distr(chrom, cc, k, dname)
		plot_oligo_distance(chrom, cc, k, dname)

	# Generate downloadable zipped files ---------------------------------------
	log(' >>> Compressing.', lpath)

	# Compress main query folder
	data = (outdir, query_id)
	zipf = zipfile.ZipFile('%s../%s.zip' % data, 'w',
		zipfile.ZIP_DEFLATED)
	zipdir(outdir, zipf)
	zipf.close()
	os.rename('%s../%s.zip' % data, '%s%s.zip' % data, )

	# Compress single candidates
	for ci in range(len(candidates)):
		oname = '%scandidates/' % outdir
		dname = '%s/probe_%d' % (oname, ci)
		zipf = zipfile.ZipFile('%s.zip' % dname, 'w', zipfile.ZIP_DEFLATED)
		zipdir(dname, zipf)
		zipf.close()

def run_multi_probe(dbpath, lpath, elpath,
	chrom, start, end, k, n_oligo, min_d, win_shift,
	f1_thr, feats_order, feats = None, verbose = None):
	'''Run single probe query.

	Args:
		dbpath (string): database folder path.
		lpath (string):  log path.
		elpath (string): error log path.
		chrom (int): chromosome in ChrXX format.
		start (int): probe range starting position.
		end (int): probe range ending position.
		n_oligo (int): number of oligo per probe.
		min_d (int): minimum distance between consecutive oligos.
		win_shift (float): fraction of window size for window shift.
		f1_thr (float): threshold of the first feature filter.
		feats (list): feature names.
		feats_order (list<int>): order of features.
		k (int): oligo size in nt.

	Returns:
		probe_sets (list): ranked list of probe set candidate tuples.
							(candidates, fvs, cseq, [spread])
	'''

	if type(None) is type(feats):
		feats = ['size', 'centrality', 'spread']
	if type(None) is type(verbose):
		verbose = True

	# Design multi probe -------------------------------------------------------
	if verbose: log('\n* MULTI PROBE DESIGN *\n', lpath)
	if verbose: log('~ Database: ' + dbpath[:-1] + '\n', lpath)

	# Find all probes in the region --------------------------------------------

	# Check window size
	if not check_window(start, end, get_min_size(n_oligo, k, min_d)):
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: too many oligos/probes were requested,'
		msg += ' or the specified window was too small.'
		log(msg, elpath)
		sys.exit()

	# Extract oligo positions
	if verbose: log(' · Extracting oligo positions.', lpath)
	poss = subset_db(get_chromosome(dbpath, chrom), start, end)

	# Exit if no oligos were found
	if 0 == len(poss):
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: no oligos found in %s:%i-%i.' % (chrom, start, end)
		log(msg, elpath)
		sys.exit()

	# Divide sets
	if verbose: log(' · Identifying candidate probes.', lpath)
	candidates = get_probe_candidates(poss, n_oligo)
	n_candidates = len(candidates)
	if verbose:
		msg = ' >>> Found ' + str(n_candidates) + ' probe candidates.'
		log(msg, lpath)

	# Exit if no candidate probes were found
	if 0 == n_candidates:
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: no candidate probes found '
		msg += 'in %s:%i-%i.' % (chrom, start, end)
		log(msg, elpath)
		sys.exit()

	# Check number of found probes
	if n_candidates < n_probes:
		# Not enough probes
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: too many probes were requested,'
		msg += ' or the specified window was too small.'
		log(msg, elpath)
		sys.exit()

	# Calculate features (id, start, end, features...) -------------------------
	fvs = np.zeros((len(candidates), len(feats) + 3))

	# Calculate first feature
	f1 = feats[feats_order[0]]
	f2 = feats[feats_order[1]]
	f3 = feats[feats_order[2]]
	if verbose: log(' · Calculating features.', lpath)
	for ci in range(len(candidates)):
		fvs[ci, 0] = ci
		fvs[ci, 1] = min(candidates[ci])
		fvs[ci, 2] = max(candidates[ci])
		fvs[ci, 3] = calc_feature(f1,
			probe = candidates[ci],
			k = k, start = start, end = end)
		fvs[ci, 4] = calc_feature(f2,
			probe = candidates[ci],
			k = k, start = start, end = end)
		fvs[ci, 5] = calc_feature(f3,
			probe = candidates[ci],
			k = k, start = start, end = end)

	# Retrieve sequence of the whole window ------------------------------------
	if verbose: log(' · Retrieving oligo sequences.', lpath)

	# Select window borders
	sstart = min([min(c) for c in candidates])
	sstop = max([max(c) for c in candidates]) + k
	
	# Get window sequence
	seq = get_seq(chrom, sstart, sstop)

	# Retrieve oligo sequences
	cseq = []
	for c in candidates:
		cseq.append([seq[(i - sstart):(i - sstart + k)] for i in c])

	# Group probes into 'all' possible probe sets-------------------------------
	
	if n_candidates == n_probes:
		# Only one probe set is present

		probe_set = {}
		probe_set['candidates'] = candidates
		probe_set['feats'] = fvs
		probe_set['seq'] = cseq
		probe_set['spread'] = []
		probe_set['windows'] = []
		probe_set['empty_windows'] = []
		probe_sets = [probe_set]
	else:
		# Define windows -------------------------------------------------------

		if verbose: log(' · Building probe windows.', lpath)
		window_sets = []		
		wsize = int((end - start) / float(n_probes + 1))
		wstarts = np.array(range(start, end, wsize))[:-1]
		if not 0 == (end - start) % wsize:
			wstarts = wstarts[:-1]
		if verbose: log(' >>> Built %d windows.' % len(wstarts), lpath)

		# Shifts
		shift = max(int(win_shift * wsize), min_d + k)
		if verbose: log(' >>> Shift: %d' % shift, lpath)

		for s in range(0, wsize, shift):
			window_sets.append(wstarts + s)
		if verbose:
			msg = ' · Will evaluate %d possible probe sets.' % len(window_sets)
			log(msg, lpath)

		# Form a probe set per window set --------------------------------------
		probe_set_signatures = []
		probe_sets = []
		for wsi in range(len(window_sets)):
			if verbose: log('  ~ Window set #%d' % (wsi), lpath)
			window_set = window_sets[wsi]
			farray = np.zeros((len(window_set), len(feats)+3))
			# Probes, features, sequences, spread, set, empty windows
			probe_set = {}
			probe_set['candidates'] = []
			probe_set['feats'] = farray
			probe_set['seq'] = []
			probe_set['spread'] = []
			probe_set['windows'] = window_set
			probe_set['empty_windows'] = []
			
			for wi in range(len(window_set)):
				window = (window_set[wi], window_set[wi] + wsize - 1)
				
				# Find probe candidates in the window
				subset = fvs[np.where(fvs[:, 1] >= window[0])]
				subset = subset[np.where((subset[:, 2] + k) <= window[1])]
				if 0 == subset.shape[0]:
					probe_set['empty_windows'].append(wi)
					if verbose:
						# Count oligos in the window
						oin = poss >= window[0]
						oin = np.logical_and(oin, poss <= window[1])
						oin = np.where(oin)
						data = (wi + 1, window[0], window[1], len(oin[0]))
						msg = '  ~~> Empty window #%d (%d-%d), %d oligos'
						log(msg % data, lpath)
				else:
					# Find best probe candidates (f1)
					selected = select_range_feature(subset[:, 3], f1_thr, f1)
					subset = subset[np.array(selected), :]

					# Rank (f2)
					rank = rank_feature(subset[:, 4], f2)
					subset = subset[rank, :]
					
					# Save candidate
					cc = candidates[int(subset[0, 0])]
					probe_set['candidates'].append(cc)
					probe_set['feats'][wi, :] = subset[0, :]
					probe_set['seq'].append(cseq[int(subset[0, 0])])
			
			# Re-size feats based on # of empty windows
			nprobes = len(window_set) - len(probe_set['empty_windows'])
			probe_set['feats'] = probe_set['feats'][:nprobes, :]

			# Add if not already added, and if a probe per window was found
			if not type(None) == type(probe_set):
				signs = probe_set['feats'][:, 0].tolist()
				if not signs in probe_set_signatures:
					signs = probe_set['feats'][:, 0].tolist()
					probe_set_signatures.append(signs)
					probe_sets.append(probe_set)

		if verbose:
			log(' >>> Found %d probe set candidates.' % len(probe_sets), lpath)

	# Check if any probe set was found
	if 0 == len(probe_sets):
		if verbose: log(' · No probe set found.', lpath)
		return(probe_sets)

	# Compare and rank probe sets-----------------------------------------------
	if verbose:
		log(' · Calculating probe sets spread.', lpath)

	# Calculate spread per probe set
	for pi in range(len(probe_sets)):
		probe_set = probe_sets[pi]
		starts = probe_set['feats'][:, 1]
		ends = probe_set['feats'][:, 2]

		probe_sets[pi]['spread'].append(calc_multi_probe_spread(starts, ends))

	# Rank
	sets_spread = [probe_sets[i]['spread'][0] for i in range(len(probe_sets))]
	sets_spread = np.array(sets_spread)
	ranked = rank_feature(sets_spread, 'spread')
	probe_sets = [probe_sets[i] for i in ranked]

	if verbose:
		msg = ' >>> Identified most homogeneous probe set: #%d' % ranked[0]
		log(msg, lpath)

	# Close --------------------------------------------------------------------
	return(probe_sets)

def output_multi_probe(query_id, outdir, lpath, chrom, start, end, k,
	probe_sets, feats, feats_order):
	'''Output single probe data.

	Args:
		query_id (string): query ID.
		outdir (string): query output directory path.
		lpath (string):  log path.
		chrom (int): chromosome in ChrXX format.
		start (int): probe range starting position.
		end (int): probe range ending position.
		k (int): oligo size in nt.
		probe_sets (list): ranked list of probe set candidate tuples.
		feats (list): feature names.
		feats_order (list<int>): order of features.

	Returns:
		None
	'''

	# Output -------------------------------------------------------------------
	log(' · Preparing output.', lpath)

	# Create candidate set folders
	for ci in range(len(probe_sets)):
		dname = outdir + 'candidates/set_' + str(ci)
		if not os.path.isdir(dname):
			os.makedirs(dname)

	# Identify features
	f1 = feats[feats_order[0]]
	f2 = feats[feats_order[1]]
	f3 = feats[feats_order[2]]

	# Generate recap table for query -------------------------------------------
	log(' >>> Generating general recap table.', lpath)

	f = open(outdir + 'sets.tsv', 'a+')

	# Table header
	head = 'set\tchr\tstart\tend\tn_probes\tspread'
	f.write(head + '\n')

	for ci in range(len(probe_sets)):
		cc = probe_sets[ci]

		# Retrieve oligo positions
		oligos = []
		cand = cc['candidates']
		[oligos.extend(cand[i].tolist()) for i in range(len(cand))]

		# Table content
		spread = cc['spread'][0]
		cdata = [ci, chrom, min(oligos), max(oligos) + k, len(cand), spread]
		f.write('%d\t%s\t%d\t%d\t%d\t%f\n' % tuple(cdata))

	f.close()

	# Generate a fasta file per candidate --------------------------------------
	log(' >>> Generating candidates fasta files.', lpath)

	for ci in range(len(probe_sets)):
		cc = probe_sets[ci]
		pname = 'set_' + str(ci)
		dname = outdir + 'candidates/' + pname + '/'
		f = open(dname + pname + '.fa', 'a+')

		for pi in range(len(cc['feats'])):
			for oi in range(len(cc['feats'][pi])):
				cand = cc['candidates']
				data = (pi + 1, oi + 1,
					chrom, cand[pi][oi], cand[pi][oi] + k, k)
				head = '> Probe_%d Oligo_%d %s:%d-%d %d' % data
				f.write(head)
				f.write('\n' + cc['seq'][pi][oi].upper() + '\n')

		f.close()

	# Generate a bed file per candidate ----------------------------------------
	log(' >>> Generating candidates bed files.', lpath)

	for ci in range(len(probe_sets)):
		cc = probe_sets[ci]
		cand = cc['candidates']
		pname = 'set_' + str(ci)
		dname = outdir + 'candidates/' + pname + '/'
		f = open(dname + pname + '.bed', 'a+')

		for pi in range(len(cc['seq'])):
			for oi in range(len(cc['seq'][pi])):
				data = (chrom, cand[pi][oi], cand[pi][oi] + k, k)
				head = '%s\t%d\t%d\t%d\n' % data
				f.write(head)

		f.close()

	# Generate config per candidate --------------------------------------------
	log(' >>> Generating candidates config file.', lpath)

	for ci in range(len(probe_sets)):
		cc = probe_sets[ci]
		cand = cc['candidates']
		dname = outdir + 'candidates/set_' + str(ci)

		# Retrieve oligo positions
		oligos = []
		[oligos.extend(cand[i].tolist()) for i in range(len(cand))]

		f = open(dname + '/config', 'a+')
		
		f.write('chr\t%s\n' % (chrom,))
		f.write('start\t%d\n' % (min(oligos),))
		f.write('stop\t%d\n' % (max(oligos) + k,))
		f.write('k\t%d\n' % (k,))
		f.write('n_probes\t%d\n' % (len(cand),))
		f.write('n_oligo\t%d\n' % (len(cand[0]),))
		f.write('%s\t%f\n' % ('spread', cc['spread'][0]))

		f.close()

	# Generate plots per candidate ---------------------------------------------
	log(' >>> Plotting candidates.', lpath)

	for ci in range(len(probe_sets)):
		cc = probe_sets[ci]
		dname = '%scandidates/set_%d/' % (outdir, ci)
		plot_probe_set(chrom, start, end, k, cc, dname)
		plot_probe_distr(chrom, cc['candidates'], k, dname)
		plot_probe_distance(chrom, cc['candidates'], k, dname)

	# Generate downloadable zipped files ---------------------------------------
	log(' >>> Compressing.', lpath)

	# Compress main query folder
	data = (outdir, query_id)
	zipf = zipfile.ZipFile('%s../%s.zip' % data, 'w',
		zipfile.ZIP_DEFLATED)
	zipdir(outdir, zipf)
	zipf.close()
	os.rename('%s../%s.zip' % data, '%s%s.zip' % data, )

	# Compress single candidates
	for ci in range(len(probe_sets)):
		oname = '%scandidates/' % outdir
		dname = '%s/set_%d' % (oname, ci)
		zipf = zipfile.ZipFile('%s.zip' % dname, 'w', zipfile.ZIP_DEFLATED)
		zipdir(dname, zipf)
		zipf.close()


# RUN ==========================================================================

# Test internet connection
try:
	uri = 'http://www.google.se'
	file = urllib2.urlopen(uri)
	file.close()
except:
	msg = '\n(╯°□°)╯︵ ┻━┻\n'
	msg += 'ERROR: no internet connection detected.'
	print(msg)
	sys.exit()

# Add trailing slash
dbpath = add_trailing_slash(dbpath)
outdir = add_trailing_slash(outdir)

# Create query folder if not existent
if not os.path.isdir(outdir):
	os.makedirs(outdir)

# Set log path
outdir = add_trailing_slash(outdir + query_id)
lpath = outdir + 'log'
elpath = outdir + 'ERROR'

# Check that query is new
if os.path.isdir(outdir):
	if not force_mode:
		msg = '(╯°□°)╯︵ ┻━┻\n'
		msg += 'ERROR: query already run.\n'
		msg += 'Use the -f option to avoid this error.'
		print(msg)
		sys.exit()
	else:
		msg = 'WARNING: query already run. Overwriting previous run.'
		print(msg)

		# Delete previous run
		shutil.rmtree(outdir)
		os.makedirs(outdir)
else:
	os.makedirs(outdir)

# Pre-output -------------------------------------------------------------------

# Save command line
log(' >>> Saving command line.', lpath)
f = open(outdir + 'cmd', 'w+')
f.write(' '.join(sys.argv))
f.close()

# Generate config file for query
log(' >>> Generating general config file.', lpath)

f = open(outdir + 'config.tsv', 'a+')

f.write('query_id\t' + str(query_id) + '\n')
f.write('name\t' + str(name) + '\n')
f.write('description\t' + str(description) + '\n')
f.write('max_probes\t' + str(max_probes) + '\n')
f.write('force_mode\t' + str(force_mode) + '\n')
f.write('chrom\t' + str(chrom) + '\n')
f.write('start\t' + str(start) + '\n')
f.write('end\t' + str(end) + '\n')
f.write('n_probes\t' + str(n_probes) + '\n')
f.write('n_oligo\t' + str(n_oligo) + '\n')
f.write('k\t' + str(k) + '\n')
f.write('min_d\t' + str(min_d) + '\n')
f.write('f1_thr\t' + str(f1_thr) + '\n')
f.write('win_shift\t' + str(win_shift) + '\n')
f.write('dbpath\t' + str(dbpath)[:-1] + '\n')
for i in range(len(feats_order)):
	f.write('f' + str(i + 1) + '\t' + feats[feats_order[i]] + '\n')

f.close()

# Check that start is smaller than end
if not start < end:
	msg = '(╯°□°)╯︵ ┻━┻\n'
	msg += 'ERROR: window\'s start should be smaller than its end.'
	log(msg, elpath)
	sys.exit()

# Select design algorithm
if is_single_probe(n_probes):
	# Design single probes -----------------------------------------------------

	# Find single probe
	(candidates, fvs, cseq) = run_single_probe(dbpath, outdir, lpath, elpath,
		chrom, start, end, k, n_oligo, min_d, max_probes,
		f1_thr, feats_order, feats)

	# Output single probe
	output_single_probe(query_id, outdir, lpath, chrom, start, end, k,
		candidates, cseq, feats, feats_order, fvs)
else:
	# Design multiple probes ---------------------------------------------------

	# Find multi probe
	probe_sets = run_multi_probe(dbpath, lpath, elpath, chrom, start, end, k,
		n_oligo, min_d, win_shift, f1_thr, feats_order)

	# Output multi probe
	output_multi_probe(query_id, outdir, lpath, chrom, start, end, k,
		probe_sets, feats, feats_order)

# END ==========================================================================

log('\n~ END ~\n', lpath)
done(outdir)
sys.exit()

################################################################################
