"""Output-panel för att visa programresultat.

Visar stdout och stderr med färgkodning.
"""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Pango


class OutputPanel(Gtk.Box):
    """Panel som visar programkörningens output."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)

        # Rubrik
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.set_margin_start(8)
        header.set_margin_end(8)
        header.set_margin_top(4)
        header.set_margin_bottom(4)

        label = Gtk.Label(label="Resultat")
        label.add_css_class("heading")
        header.append(label)

        # Rensa-knapp
        clear_btn = Gtk.Button(label="Rensa")
        clear_btn.set_halign(Gtk.Align.END)
        clear_btn.set_hexpand(True)
        clear_btn.connect("clicked", lambda _: self.clear())
        header.append(clear_btn)

        self.append(header)

        # Separator
        self.append(Gtk.Separator())

        # Scrolled textvy
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        self._textview = Gtk.TextView()
        self._textview.set_editable(False)
        self._textview.set_cursor_visible(False)
        self._textview.set_monospace(True)
        self._textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._textview.set_left_margin(12)
        self._textview.set_right_margin(12)
        self._textview.set_top_margin(8)
        self._textview.set_bottom_margin(8)

        # CSS för fontstorlek
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(
            "textview { font-size: 14px; }"
        )
        self._textview.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Text-taggar för färgkodning
        self._buffer = self._textview.get_buffer()
        self._tag_stdout = self._buffer.create_tag(
            "stdout", foreground="#2e7d32"
        )
        self._tag_stderr = self._buffer.create_tag(
            "stderr", foreground="#c62828", weight=Pango.Weight.BOLD
        )
        self._tag_info = self._buffer.create_tag(
            "info", foreground="#1565c0", style=Pango.Style.ITALIC
        )
        self._tag_success = self._buffer.create_tag(
            "success", foreground="#2e7d32", weight=Pango.Weight.BOLD
        )

        scrolled.set_child(self._textview)
        self.append(scrolled)

    def append_stdout(self, text: str):
        """Lägg till stdout-text."""
        end = self._buffer.get_end_iter()
        self._buffer.insert_with_tags(end, text, self._tag_stdout)
        self._scroll_to_end()

    def append_stderr(self, text: str):
        """Lägg till stderr-text (felmeddelanden)."""
        end = self._buffer.get_end_iter()
        self._buffer.insert_with_tags(end, text, self._tag_stderr)
        self._scroll_to_end()

    def append_info(self, text: str):
        """Lägg till informationstext."""
        end = self._buffer.get_end_iter()
        self._buffer.insert_with_tags(end, text, self._tag_info)
        self._scroll_to_end()

    def append_success(self, text: str):
        """Lägg till framgångstext."""
        end = self._buffer.get_end_iter()
        self._buffer.insert_with_tags(end, text, self._tag_success)
        self._scroll_to_end()

    def clear(self):
        """Rensa all output."""
        self._buffer.set_text("")

    def _scroll_to_end(self):
        """Scrolla till slutet av outputen."""
        end = self._buffer.get_end_iter()
        self._textview.scroll_to_iter(end, 0.0, False, 0.0, 1.0)
