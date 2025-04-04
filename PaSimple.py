#! /usr/bin/python
import gi, subprocess
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

class MyApp(Gtk.Application):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.connect('activate', self.on_activate)

	def on_activate(self, app):
		# Create a Builder
		builder: Gtk.Builder = Gtk.Builder()
		builder.add_from_file("PaSimple.cmb")

		# Obtain and show the main window
		self.win: Gtk.Window = builder.get_object("main_window")
		self.side_bar: Gtk.ActionBar = builder.get_object("side_bar")
		self.header_bar: Gtk.HeaderBar = builder.get_object("header_bar")
		self.win.set_application(self)
		self.win.set_icon_name("text-editor")
		self.win.present()

app: MyApp = MyApp(application_id="org.elMate.package-manager")
app.run(sys.argv)
