#! /usr/bin/python
import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

class PackageBox(Gtk.Box):
	def __init__(self, name, version, description, installed, repo, on_toggle, on_info):
		super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

		# Pobieranie ikony z obecnego motywu GTK
		icon = Gtk.Image()
		theme = Gtk.IconTheme.get_default()
		if theme.has_icon(name):
			icon.set_from_icon_name(name, Gtk.IconSize.LARGE_TOOLBAR)
		else: icon.set_from_icon_name("package", Gtk.IconSize.LARGE_TOOLBAR)

		self.pack_start(icon, False, False, 0)

		# Informacje o pakiecie
		label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
		name_label = Gtk.Label()
		name_label.set_markup(f"<b>{name}</b> ({repo})")
		name_label.set_xalign(0)

		version_label = Gtk.Label(label=f"Version: {version}")
		version_label.set_xalign(0)

		description_label = Gtk.Label()
		if len(description) > 80:
			description_label.label = description[:80] + "..."
		else: description_label.label = description

		description_label.set_xalign(0)
		description_label.set_max_width_chars(80)
		description_label.set_ellipsize(3)

		label_box.pack_start(name_label, False, False, 0)
		label_box.pack_start(version_label, False, False, 0)
		label_box.pack_start(description_label, False, False, 0)
		self.pack_start(label_box, True, True, 0)

		# Przycisk "Info"
		info_button = Gtk.Button(label="Info")
		info_button.connect("clicked", on_info, name, repo)
		self.pack_start(info_button, False, True, 0)

		# Przycisk Install / Remove (dodaje do kolejki operacji)
		self.toggle_button = Gtk.ToggleButton(
			label = "Remove" if installed else "Install")
		self.toggle_button.connect("toggled", on_toggle, name, installed)
		self.pack_start(self.toggle_button, False, False, 0)

class PaSimple(Gtk.Window):
	def __init__(self):
		super().__init__(title="PaSimple - Package Manager")
		self.set_default_size(800, 600)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.add(vbox)

		# Pole wyszukiwania
		search_box = Gtk.Box(spacing=5)
		self.search_entry = Gtk.Entry()
		self.search_entry.set_placeholder_text("Search for packages...")
		self.search_entry.connect("activate", self.on_search)
		search_box.pack_start(self.search_entry, True, True, 0)

		search_button = Gtk.Button(label="Search")
		search_button.connect("clicked", self.on_search)
		search_box.pack_start(search_button, False, False, 0)
		vbox.pack_start(search_box, False, False, 0)

		# Przewijana lista pakietów
		self.package_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_policy(
			Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled_window.add(self.package_list)
		vbox.pack_start(scrolled_window, True, True, 0)

		# Lista operacji do zatwierdzenia
		self.pending_operations = []
		self.pending_pkgs = []

		# Przycisk zatwierdzenia operacji
		action_box = Gtk.Box(spacing=5)
		self.apply_button = Gtk.Button(label="Apply Changes")
		self.apply_button.connect("clicked", self.on_apply_changes)
		self.apply_button.set_sensitive(False)

		self.cancel_button = Gtk.Button(label="Cancel")
		self.cancel_button.connect("clicked", self.on_cancel_operations)
		self.cancel_button.set_sensitive(False)

		action_box.pack_start(self.apply_button, True, True, 0)
		action_box.pack_start(self.cancel_button, True, True, 0)
		vbox.pack_start(action_box, False, False, 0)

		# Domyślnie wczytaj wszystkie pakiety
		# self.on_search(None)

	def on_cancel_operations():
		self.pending_operations = []
		self.pending_pkgs = []

	def load_installed_packages(self):
		""" Pobiera listę zainstalowanych pakietów """
		try:
			result = subprocess.run(["yay", "-Qq"], capture_output=True, text=True)
			return set(result.stdout.splitlines())
		except Exception as e:
			print(f"Error checking installed packages: {e}")
			return set()
		
	def on_search(self, widget):
		""" Wyszukuje pakiety w repo i AUR """
		# Czyści listę
		query = self.search_entry.get_text().strip()
		if query == "": return
		installed_packages = self.load_installed_packages()
		
		## Jeśli nie wpisano nic, pokaż wszystkie pakiety
		# if query == "": search_command = ["yay", "-Ssq"]
		# else: search_command = ["yay", "-Ss", query]
		search_command = ["yay", "-Ss", query]

		try:
			result = subprocess.run(search_command, capture_output=True, text=True)
			lines = result.stdout.splitlines()

			packages = []
			i = 0
			while i < len(lines):
				if lines[i].startswith(" "):  # Opis pakietu
					i += 1
					continue

				parts = lines[i].split(" ")
				repo_pkg = parts[0].split("/")
				if len(repo_pkg) > 1:
					repo = repo_pkg[0]
					name = repo_pkg[1]
				else:
					repo = "Unknown"
					name = repo_pkg[0]

				if len(parts) > 1:
					version = parts[1]
				else: version = "N/A"

				if i + 1 < len(lines) and lines[i + 1].startswith("    "):
					description = lines[i + 1].strip()
				else: description = ""

				installed = name in installed_packages
				packages.append((name, version, description, installed, repo))
				i += 1

			installed = name in installed_packages
			packages.append((name, version, description, installed, repo))

			# Sortowanie – najpierw dokładne dopasowania, potem podobne
			packages.sort(key=lambda p: (not p[0] == query, p[0]))

			pkg_boxes = []
			for pkg in packages:
				if (pkg[0], pkg[-1]) in pkg_boxes: continue
				else: pkg_boxes.append((pkg[0], pkg[-1]))
				pkg_box = PackageBox(*pkg, self.on_toggle, self.on_info)
				if pkg in self.pending_pkgs: pkg_box.toggle_button.set_active(True)
				self.package_list.pack_start(pkg_box, False, False, 0)

			self.package_list.show_all()

		except Exception as e:
			print(f"Error searching packages: {e}")

	def on_toggle(self, button, package_name, was_installed):
		""" Obsługuje przełączanie stanu pakietu (dodaje do kolejki operacji) """
		if button.get_active():
			if button.label == "Install":
				self.pending_operations.append(("install", package_name))
			elif button.label == "Remove":
				self.pending_operations.append(("remove", package_name))
			self.pending_pkgs.append(package_name)

		self.apply_button.set_sensitive(True)
		self.cancel_button.set_sensitive(True)

	def on_apply_changes(self, widget):
		""" Wykonuje zaplanowane operacje """
		if not self.pending_operations: return

		install_packages = []
		remove_packages = []

		for op, pkg in self.pending_operations:
			if op == "install": install_packages.append(pkg)
			elif op == "remove": remove_packages.append(pkg)

		confirmed = self.show_confirmation_dialog(
			install_packages, remove_packages)
		
		if confirmed:
			if install_packages: subprocess.run(
				["pkexec", "yay", "-S", "--noconfirm"] + install_packages)
			if remove_packages: subprocess.run(
				["pkexec", "yay", "-R", "--noconfirm"] + remove_packages)

			self.pending_operations.clear()
			self.apply_button.set_sensitive(False)
			self.cancel_button.set_sensitive(False)
			self.on_search(None) # Odśwież listę pakietów

	def on_info(self, widget, package_name, repo):
		"""Wyświetla informacje o pakiecie (z repozytoriów lub AUR)"""
		result = subprocess.run(
			["yay", "-Si", package_name], capture_output=True, text=True)
		info_text = result.stdout.strip()
		
		if not info_text: info_text = "No package information found."
		self.show_info_dialog(info_text)

	def show_info_dialog(self, text):
		"""Wyświetla info o pakiecie w osobnym oknie z przewijanym obszarem"""
		info_window = Gtk.Window(title="Package Information")
		info_window.set_default_size(600, 400)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		info_window.add(vbox)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_policy(
			Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled_window.set_vexpand(True)

		textview = Gtk.TextView()
		textview.set_editable(False)
		textview.set_wrap_mode(Gtk.WrapMode.WORD)
		buffer = textview.get_buffer()
		buffer.set_text(text)

		scrolled_window.add(textview)
		vbox.pack_start(scrolled_window, True, True, 0)

		close_button = Gtk.Button(label="Close")
		close_button.connect("clicked", lambda w: info_window.destroy())
		vbox.pack_start(close_button, False, False, 0)

		info_window.show_all()

# Uruchomienie aplikacji
win = PaSimple()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
