"""Kodeditor med svensk syntaxhighlighting.

Använder GtkSourceView 5 för en fullfjädrad kodeditor
med stöd för svenska programmeringsnyckelord.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GtkSource", "5")

from gi.repository import Gtk, GtkSource, Pango


class CodeEditor(Gtk.ScrolledWindow):
    """Kodeditor med svensk syntaxhighlighting."""

    def __init__(self):
        super().__init__()
        self.set_vexpand(True)
        self.set_hexpand(True)

        # Skapa SourceView
        self._buffer = GtkSource.Buffer()
        self._view = GtkSource.View(buffer=self._buffer)

        # Editor-inställningar
        self._view.set_show_line_numbers(True)
        self._view.set_auto_indent(True)
        self._view.set_indent_on_tab(True)
        self._view.set_tab_width(4)
        self._view.set_insert_spaces_instead_of_tabs(True)
        self._view.set_highlight_current_line(True)
        self._view.set_monospace(True)
        self._view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        # Stor text för barn
        font_desc = Pango.FontDescription.from_string("Monospace 16")
        attrs = Pango.AttrList()
        attrs.insert(Pango.attr_font_desc_new(font_desc))

        # Margin för läsbarhet
        self._view.set_left_margin(8)
        self._view.set_right_margin(8)
        self._view.set_top_margin(8)
        self._view.set_bottom_margin(8)

        # Konfigurera syntaxhighlighting
        self._setup_highlighting()

        # Lägg till SourceView
        self.set_child(self._view)

        # Lägg till CSS för fontstorlek
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(
            "textview { font-family: monospace; font-size: 16px; }"
        )
        self._view.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _setup_highlighting(self):
        """Konfigurera svensk syntaxhighlighting."""
        lm = GtkSource.LanguageManager.get_default()

        # Försök ladda vår anpassade svenskpython-språkdefinition
        import os
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "language-specs"
        )
        search_path = list(lm.get_search_path())
        if data_dir not in search_path:
            search_path.insert(0, data_dir)
            lm.set_search_path(search_path)

        lang = lm.get_language("svenskpython")
        if lang:
            self._buffer.set_language(lang)
        else:
            # Fallback till Python-highlighting
            lang = lm.get_language("python3") or lm.get_language("python")
            if lang:
                self._buffer.set_language(lang)

        # Färgschema
        sm = GtkSource.StyleSchemeManager.get_default()
        scheme = sm.get_scheme("Adwaita")
        if scheme:
            self._buffer.set_style_scheme(scheme)

    def get_text(self) -> str:
        """Hämta all text från editorn."""
        start = self._buffer.get_start_iter()
        end = self._buffer.get_end_iter()
        return self._buffer.get_text(start, end, True)

    def set_text(self, text: str):
        """Sätt text i editorn."""
        self._buffer.set_text(text)

    def clear(self):
        """Rensa editorn."""
        self._buffer.set_text("")

    def highlight_line(self, line_number: int, highlight: bool = True):
        """Markera en rad (för debuggern)."""
        if highlight:
            iter_ = self._buffer.get_iter_at_line(line_number - 1)
            self._buffer.place_cursor(iter_)
            self._view.scroll_to_iter(iter_, 0.2, False, 0, 0.5)

    def get_buffer(self) -> GtkSource.Buffer:
        """Hämta buffer för extern åtkomst."""
        return self._buffer

    def get_view(self) -> GtkSource.View:
        """Hämta view för extern åtkomst."""
        return self._view
