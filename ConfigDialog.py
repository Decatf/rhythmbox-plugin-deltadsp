#    ConfigDialog.py
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

import rb

from gi.repository import GObject, Gtk, Gio, PeasGtk
from gi.repository import RB

GAIN_DEFAULT = 100
GAIN_MIN = 0
GAIN_MAX = 200

class DeltaDspConfig(GObject.Object, PeasGtk.Configurable):
	__gtype_name__ = 'DeltaDspConfig'
	object = GObject.property(type=GObject.Object)

	def do_create_configure_widget(self):
		self.settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.deltadsp")

		ui_file = rb.find_plugin_file(self, "deltadsp-prefs_widget.ui")
		if ui_file == None:
			return None;

		self.builder = Gtk.Builder()
		self.builder.add_from_file(ui_file)

		dialog_widget = self.builder.get_object("dialog-vbox")

		gain = self.builder.get_object("gain_scale")
		if gain != None:
			gain.add_mark(GAIN_DEFAULT, 1, str(GAIN_DEFAULT));
			gain.add_mark(GAIN_MIN, 1, str(GAIN_MIN));
			gain.add_mark(GAIN_MAX, 1, str(GAIN_MAX));

			gain_adj = self.builder.get_object("gain_adjustment")
			if gain_adj != None:
				gain_adj.set_value(self.settings['gain'])

			self.settings.bind("gain", gain.props.adjustment, "value", Gio.SettingsBindFlags.GET)
			gain.connect("value-changed", self.gain_changed_cb)
			
		if self.settings['has-gstdelta'] is False:
			gain.set_sensitive(False)
			gain_label = self.builder.get_object("gain_label")
			gain_label.set_sensitive(False)
			msg_label = self.builder.get_object("msg_label")
			msg_label.set_label("Error: 'GStreamer delta' plugin not found. \nInstall gstreamer1.0-delta on the system to enable this plugin. ")

		return dialog_widget

	def gain_changed_cb(self, gain):
		RB.settings_delayed_sync(self.settings, self.sync_gain, gain)

	def sync_gain(self, settings, gain):
		v = gain.get_value()
		#print "gain changed to %f" % v
		settings['gain'] = v
