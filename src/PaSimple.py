#! /usr/bin/python
import gi
import subprocess, sys

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

class PaSimple(Gtk.Application):
	def __init__(self):
		super().__init__(application_id="com.example.PaSimple")
		self.builder = Gtk.Builder()
		self.builder.add_from_file("ui/pasimple.ui")

		self.window = self.builder.get_object("main_window")

		self.search_entry = self.builder.get_object("search_entry")
		self.apply_button = self.builder.get_object("apply_button")
		self.cancel_button = self.builder.get_object("cancel_button")

		self.search_entry.connect("activate", self.on_search)
		self.apply_button.connect("clicked", self.on_apply_changes)
		self.cancel_button.connect("clicked", self.on_cancel_operations)

		self.pending_operations = []
		self.pending_pkgs = []

	def on_search(self, widget):
		query = self.search_entry.get_text().strip()
		if not query:
			return
		# Implement search logic here
		print(f"Searching for: {query}")

	def on_apply_changes(self, widget):
		if not self.pending_operations:
			return
		print("Applying changes...")
		# Implement apply logic here

	def on_cancel_operations(self, widget):
		self.pending_operations.clear()
		self.pending_pkgs.clear()
		print("Cancelled operations.")

	def do_activate(self):
		self.window.set_application(self)
		self.window.show()

app = PaSimple()
app.run(sys.argv)
