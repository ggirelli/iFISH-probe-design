#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Web-Server
# 
# TODO:
# 	- Fix behavior when run from different working directory. (and in sections)
# 
# ------------------------------------------------------------------------------


# DEPENDENCIES =================================================================

import argparse
import bottle as bot
import os
import paste
import sections as sec

# INPUT ========================================================================

# Add script description
parser = argparse.ArgumentParser(
	description = 'Run WebServer.'
)

# Add params
parser.add_argument('--url', metavar = 'url', type = str, nargs = 1,
	default = ['0.0.0.0'], help = 'Web Server URL.')
parser.add_argument('--port', metavar = 'port', type = int, nargs = 1,
	default = [8080], help = 'Web Server port.')

# Parse arguments
args = parser.parse_args()

# Retrieve arguments
root_uri = args.url[0]
port = args.port[0]

# INIT =========================================================================

# Server params
root_path = os.path.dirname(os.path.realpath(__file__)) + '/'
ruri_complete = 'http://' + root_uri + ':' + str(port) + '/'

# Sections path
spath = 'sections/'

# App title
title = 'BiCro Commons'

# Add views folder to TEMPLATE_PATH
bot.TEMPLATE_PATH.append(root_path)
bot.TEMPLATE_PATH.append(root_path + 'views/')

# Start root app
root = bot.Bottle()

# ROUTES =======================================================================

# Home
@root.route('/')
@bot.view('home')
def index():
	d = {}
	d['custom_stylesheets'] = ['home.css']
	d['title'] = title
	d['description'] = title
	return d

# 404 Error
@root.error(404)
def error404(error):
	return 'Nothing here, sorry :('

# Static files -----------------------------------------------------------------

# CSS files
@root.route('/css/<path>')
def callback(path):
    return bot.static_file(path, root_path + '/css/')

# JS files
@root.route('/js/<path>')
def callback(path):
    return bot.static_file(path, root_path + '/js/')

# Fonts files
@root.route('/fonts/<path>')
def callback(path):
    return bot.static_file(path, root_path + '/fonts/')

# Images
@root.route('/images/<path>')
def callback(path):
    return bot.static_file(path, root_path + '/images/')

# Documents
@root.route('/documents/<path>')
def callback(path):
    return bot.static_file(path, root_path + '/documents/')

# Documentation ----------------------------------------------------------------

@root.route('/docs/<path:re:.*>')
def go_docs(path):
	if 0 == len(path): path = 'index.html'
	return bot.static_file(path, root_path + 'docs/_build/html/')

# Sections ---------------------------------------------------------------------

# Probe designer
root.mount('probe-design/',
	sec.probe_design.App(spath, root_path, ruri_complete, 'probe-design/'))

# RUN ==========================================================================

root.run(host = root_uri, port = port, debug = True, server = 'paste')

# END ==========================================================================

################################################################################
