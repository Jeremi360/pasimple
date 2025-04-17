import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class PackageBox(Gtk.Box):
	def __init__(self, icon, name, version, repo, description):
		super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file("ui/PackageBox.ui")

		self.icon_image = self.builder.get_object("icon_image")
		self.name_label = self.builder.get_object("name_label")
		self.version_label = self.builder.get_object("version_label")
		self.repo_label = self.builder.get_object("repo_label")
		self.description_label = self.builder.get_object("description_label")

		self.icon_image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
		self.name_label.set_text(name)
		self.version_label.set_text(version)
		self.repo_label.set_text(repo)
		self.description_label.set_text(description)

		self.pack_start(self.builder.get_object("package_box"), True, True, 0)