# -*- coding: utf8 -*-

import gi
gi.require_version('Gedit', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GObject, Gio, Gtk, Gdk, Gedit

from .core import FileBrowserSelector

class AppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.add_accelerator("<Primary><Alt>F", "win.select-current-document", None)

    def do_deactivate(self):
        self.app.remove_accelerator("win.select-current-document", None)


class WindowActivatable(GObject.Object, Gedit.WindowActivatable):
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # this basically requires the filebrowser plugin to be loaded
        # otherwise it won't activate

        try:
            bus = self.window.get_message_bus()
            msg = bus.send_sync('/plugins/filebrowser', 'get_view')
            self.view = msg.props.view

            self.activate_real()
        except TypeError:
            self.view = None

    def activate_real(self):
        self.selector = FileBrowserSelector(self.window, self.view)

        action = Gio.SimpleAction(name="select-current-document")
        action.connect('activate', self.select_current_document)
        self.window.add_action(action)

        self.view_key_handler = self.view.connect('key-press-event', self.on_view_key_press)

    def do_deactivate(self):
        if self.view:
            self.window.remove_action("indented-paste")
            self.view.disconnect(self.view_key_handler)

    def on_view_key_press(self, view, event):
        modifiers = event.state & Gtk.accelerator_get_default_mod_mask()

        if modifiers == Gdk.ModifierType.MOD1_MASK and event.keyval == Gdk.KEY_p:
            self.selector.select_parent()
            return True

        return False

    def select_current_document(self, a, p):
        self.selector.select_current_document()

