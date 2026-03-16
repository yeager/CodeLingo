"""CodeLingo - Huvudapplikation.

Gtk.Application-klass som hanterar applikationslivscykeln.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk

from codelingo import APP_ID, APP_NAME, VERSION
from codelingo.window import CodeLingoWindow


class CodeLingoApp(Adw.Application):
    """Huvudapplikation för CodeLingo."""

    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.set_resource_base_path("/se/codelingo/CodeLingo")

    def do_startup(self):
        """Initialisering vid uppstart."""
        Adw.Application.do_startup(self)

        # Registrera actions
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self._on_quit)
        self.add_action(action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self._on_about)
        self.add_action(action)

        # Ladda CSS
        self._load_css()

    def do_activate(self):
        """Skapa och visa huvudfönstret."""
        win = self.get_active_window()
        if not win:
            win = CodeLingoWindow(application=self)
        win.present()

    def _load_css(self):
        """Ladda anpassad CSS för barnvänlig design."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(CSS_DATA)
        Gtk.StyleContext.add_provider_for_display(
            self.get_active_window().get_display()
            if self.get_active_window()
            else __import__("gi.repository.Gdk", fromlist=["Gdk"]).Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _on_quit(self, _action, _param):
        """Avsluta applikationen."""
        self.quit()

    def _on_about(self, _action, _param):
        """Visa Om-dialog."""
        about = Adw.AboutWindow(
            transient_for=self.get_active_window(),
            application_name=APP_NAME,
            application_icon="applications-education",
            version=VERSION,
            developer_name="CodeLingo",
            copyright="2024 CodeLingo",
            license_type=Gtk.License.MIT_X11,
            comments="Lär barn programmera på svenska!\n\n"
                    "CodeLingo översätter svenska programmeringskommandon "
                    "till Python så att barn kan lära sig koda på sitt "
                    "modersmål.",
            website="https://github.com/codelingo",
            developers=["CodeLingo-teamet"],
        )
        about.present()


# Inbäddad CSS för barnvänlig design
CSS_DATA = """
/* CodeLingo - Barnvänlig design */

.suggested-action {
    min-height: 36px;
    min-width: 80px;
    font-weight: bold;
}

.heading {
    font-weight: bold;
}

.title-2 {
    font-size: 1.4em;
    font-weight: bold;
}

.title-3 {
    font-size: 1.2em;
    font-weight: bold;
}

.title-4 {
    font-size: 1.1em;
    font-weight: bold;
}

/* Stor, tydlig text i tutorial-panelen */
.boxed-list row {
    min-height: 60px;
}

/* Färgglad knappdesign */
button.run-button {
    background-color: #4caf50;
    color: white;
}

button.stop-button {
    background-color: #f44336;
    color: white;
}

/* Markering av aktuell rad i debuggern */
.debug-current-line {
    background-color: rgba(255, 235, 59, 0.3);
}
"""


def main():
    """Startpunkt för CodeLingo."""
    app = CodeLingoApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
