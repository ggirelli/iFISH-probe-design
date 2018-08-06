#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Description: Sample Route manager
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

from .. import routes

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

		# Pages ----------------------------------------------------------------

		# Forms ----------------------------------------------------------------

		# Errors ---------------------------------------------------------------

		return

	# Static files -------------------------------------------------------------

	# Pages --------------------------------------------------------------------

	def home(routes, self):
		'''Home-page.

		Args:
			self (App): ProbeDesigner.App instance.
		'''

		# Template dictionary
		d = self.vd

		# Page title and description
		d['title'] = self.tprefix + 'Home'

		# Local stylesheets
		d['custom_stylesheets'] = ['home.css']

		# Root stylesheets
		d['custom_root_stylesheets'] = []
		
		return(d)

	# Form reception -----------------------------------------------------------

	# Error --------------------------------------------------------------------

# END ==========================================================================

################################################################################
