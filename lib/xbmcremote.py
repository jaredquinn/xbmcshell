#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Copyright (C) 2011 Jared Quinn http://jaredquinn.info
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Implementation of XBMC's Full JSON-RPC input system.

This should continue to work as the interfaces are extended as nothing is
hard coded and the library relays the requested calls directly to the
interface.  Errors are returned.
"""

__author__ = "jared@jaredquinn.info"
__version__ = "0.1"

import json
import urllib
import urllib2
import uuid
import logging
import string 

class xbmcremote():
	""" Base class that implements the handler for all functions

	- Generic structure 
	- Calls can be made to xbmcremote.JSONInterface.Method({ params })

	"""
	def __init__(self, url):
		self.url = url
		self.use = 'interface'

	def __getattr__(self, interface):
		if interface == '_wrapper':
			return xbmcwrapper(self)

		if interface.startswith('_'):
			raise AttributeError(interface)
	
		if self.use == 'interface':	
			return xbmcrpcinterface(self, interface)
		if self.use == 'method':
			return xbmcrpcmethod(self, interface)

class xbmcrpcinterface(xbmcremote):
	
	def __init__(self, parent, name):
		xbmcremote.__init__(self, parent.url)
		self.name = name
		self.use = 'method'

class xbmcrpcmethod:

	def __init__(self, parent, name):
		self.name = name
		self.parent = parent
		self.url = parent.url
		self.logger = logging.getLogger('xbmcremote')

	def __call__(self, args = None):
		opener = urllib2.build_opener(urllib2.HTTPHandler())

		if args == None:
			args = { }

		headers = {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'}
		self.logger.debug('request headers: %s' % headers)

	 	dataObject = {
			'jsonrpc': '2.0',
			'method': '%s.%s' % (self.parent.name, self.name),
			'params': args,
			'id': 1 }

		jsondata = json.dumps(dataObject)
		self.logger.debug('jsondata: %s' % jsondata)

		request = urllib2.Request(self.url, jsondata, headers)
		try:
			response = opener.open(request)
			content = response.read(response)
			self.logger.debug('response: %s' % content)
			jdata = json.loads(content)
			result = jdata.get('result')
			error = jdata.get('error')
			if error:
				raise Exception('#%s %s' % ( error.get('code'), error.get('message') ))

		except Exception, e:
			raise Exception('xbmc:json-rpc error: %s' % str(e))

		return result

