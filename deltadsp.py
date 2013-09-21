#    deltadsp.py
#    Copyright (C) 2010 Robert Y <Decatf@gmail.com>
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
from gi.repository import GObject, Gtk, Gio, RB, Peas, Gst
from ConfigDialog import DeltaDspConfig

GST_PLUGIN_NAME = "delta"

class DeltaDspPlugin (GObject.Object, Peas.Activatable):
	__gtype_name__ = 'DeltaDspPlugin'
	object = GObject.property(type=GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.shell = self.object
		self.sp = self.shell.props.shell_player

		self.settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.deltadsp")
		self.delta = Gst.ElementFactory.make (GST_PLUGIN_NAME, None)

		if self.settings is not None:
			self.settings.connect("changed::gain", self.gain_changed_cb)
			if self.delta is not None:
				self.settings['has-gstdelta'] = True
			else:
				self.settings['has-gstdelta'] = False
		
		if self.delta is not None:
			gain = 100
			if self.settings is not None:
				gain = self.settings['gain']
			self.delta.set_property("gain", gain)
			self.delta.set_property("silent", True)

			try:
				if self.sp.get_playing():
					self.sp.stop()
					self.sp.props.player.add_filter(self.delta)
					self.sp.play()
				else:
					self.sp.props.player.add_filter(self.delta)
			except:
				pass

	def do_deactivate(self):
		if self.delta is not None:
			try:
				if self.sp.get_playing():
					self.sp.stop()
					self.sp.props.player.remove_filter(self.delta)
					self.sp.play()
				else:
					self.sp.props.player.remove_filter(self.delta)
			except:
				pass

		del self.settings
		del self.sp
		del self.shell

	def gain_changed_cb(self, settings, key):
		if self.delta is not None:
			limiter = settings[key]
			#print key + " setting is now %s" % str(limiter)
			self.delta.set_property("gain", settings[key])
