#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Date: 161117
# Description: Convert Mihaela's pipeline output (sqlite server) into a more
# 			   approachable and manageable format: a list of positions
# 			   per chromosome.
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import argparse
import os
import sqlite3

# INPUT ========================================================================

# Add script description
parser = argparse.ArgumentParser(
	description = 'Convert uniqueOligo database to chr-files.'
)

# Add params
parser.add_argument('db', metavar = 'db', type = str, nargs = 1,
	help = 'Sqlite3 database path.')
parser.add_argument('table', metavar = 'table', type = str, nargs = 1,
	help = 'Table name.')
parser.add_argument('--outdir', metavar = 'od', type = str, nargs = 1,
	default = ['.'], help = 'Database directory path.')

# Parse arguments
args = parser.parse_args()

# Retrieve arguments
dbpath = args.db[0]
table = args.table[0]
outdir = args.outdir[0]

# FUNCTIONS ====================================================================

# RUN ==========================================================================

print('\nExtracting information from unique oligo databases.')
print('Database: ' + dbpath)
print('Table: ' + table + '\n')

# Connect to databases
print(' · Connecting to database...')
conn = sqlite3.connect(dbpath)
c = conn.cursor()

# Identify chromosomes
print(' · Identifying chromosomes...')
chrlist = []
q = 'SELECT CHR FROM ' + table
for row in c.execute(q):
	if not row[0] in chrlist:
		chrlist.append(row[0])

# Create output folder
print(' · Creating output folder...')
outdir = outdir + '/' + table + '/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Extracting table per chromosome
print(' · Extracting oligo positions per chromosome...')
for chrom in chrlist:
	print(' >>> chr' + str(chrom) + ' ...')

	# Output file path
	fpath = outdir + 'chr' + str(chrom)

	# Remove file if it exists
	try:
		os.remove(fpath)
	except OSError:
		pass

	# Open file connection
	outf = open(fpath, 'a+')

	# Query to get positions
	q = 'SELECT START FROM ' + table + ' WHERE CHR=?'
	for row in c.execute(q, (chrom,)):
		# Output position
		outf.write(','.join([str(i) for i in row]) + '\n')

	# Close file connection
	outf.close()

# END ==========================================================================

print('\n~ DONE ~\n')

################################################################################
