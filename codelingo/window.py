"""Huvudfönster för CodeLingo.

Innehåller den kompletta layouten med tutorial-sidopanel,
kodeditor, output-panel och debugger-verktyg.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from codelingo.debugger import DebugState, SimpleDebugger
from codelingo.editor import CodeEditor
from codelingo.output_panel import OutputPanel
from codelingo.runner import Runner
from codelingo.translator import Translator
from codelingo.tutorials import TutorialManager
from codelingo.i18n import _


class CodeLingoWindow(Adw.ApplicationWindow):
    """Huvudfönster med komplett IDE-layout."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_("CodeLingo - Program in Swedish!"))
        self.set_default_size(1200, 800)

        # Kärn-komponenter
        self._translator = Translator()
        self._runner = Runner(timeout_seconds=5.0)
        self._debugger = SimpleDebugger()
        self._tutorial_manager = TutorialManager()
        self._current_tutorial = None
        self._current_step = 0

        # Bygg UI
        self._build_ui()

        # Ladda första tutorial
        tutorials = self._tutorial_manager.get_all()
        if tutorials:
            self._load_tutorial(tutorials[0])

    def _build_ui(self):
        """Bygg hela användargränssnittet."""
        # Huvudlayout med Adw
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar
        header = Adw.HeaderBar()
        title = Adw.WindowTitle(
            title="CodeLingo",
            subtitle="Programmera på svenska!"
        )
        header.set_title_widget(title)

        # Knappar i header
        self._run_button = Gtk.Button(label=_("Drive"))
        self._run_button.add_css_class("suggested-action")
        self._run_button.set_icon_name("media-playback-start-symbolic")
        self._run_button.set_tooltip_text("Kör programmet (Ctrl+Enter)")
        self._run_button.connect("clicked", self._on_run_clicked)

        self._debug_button = Gtk.Button(label="Debugga")
        self._debug_button.set_icon_name("find-location-symbolic")
        self._debug_button.set_tooltip_text("Stega igenom koden")
        self._debug_button.connect("clicked", self._on_debug_clicked)

        self._clear_button = Gtk.Button(icon_name="edit-clear-all-symbolic")
        self._clear_button.set_tooltip_text("Rensa allt")
        self._clear_button.connect("clicked", self._on_clear_clicked)

        # Visa Python-knapp
        self._show_python_button = Gtk.ToggleButton(label="Visa Python")
        self._show_python_button.set_tooltip_text(
            "Visa den översatta Python-koden"
        )
        self._show_python_button.connect(
            "toggled", self._on_show_python_toggled
        )

        header.pack_start(self._run_button)
        header.pack_start(self._debug_button)
        header.pack_end(self._clear_button)
        header.pack_end(self._show_python_button)

        main_box.append(header)

        # Huvudinnehåll: horisontell paned
        self._main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self._main_paned.set_vexpand(True)

        # Vänster: Tutorial-panel
        self._tutorial_panel = self._build_tutorial_panel()
        self._main_paned.set_start_child(self._tutorial_panel)
        self._main_paned.set_shrink_start_child(False)

        # Höger: Editor + Output (vertikal paned)
        right_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)

        # Editor med ram
        editor_frame = Gtk.Frame()
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        editor_label = Gtk.Label(label="Svensk kod")
        editor_label.add_css_class("heading")
        editor_label.set_margin_start(8)
        editor_label.set_margin_top(4)
        editor_label.set_margin_bottom(4)
        editor_label.set_halign(Gtk.Align.START)
        editor_box.append(editor_label)

        self._editor = CodeEditor()
        editor_box.append(self._editor)

        # Python-förhandsgranskning (dold som standard)
        self._python_revealer = Gtk.Revealer()
        self._python_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_DOWN
        )
        python_frame = Gtk.Frame(label=_("Python translation"))
        python_scroll = Gtk.ScrolledWindow()
        python_scroll.set_max_content_height(150)
        python_scroll.set_propagate_natural_height(True)

        self._python_view = Gtk.TextView()
        self._python_view.set_editable(False)
        self._python_view.set_monospace(True)
        self._python_view.set_left_margin(8)
        self._python_view.set_top_margin(4)

        css = Gtk.CssProvider()
        css.load_from_string(
            "textview { font-size: 13px; background-color: alpha(@accent_bg_color, 0.1); }"
        )
        self._python_view.get_style_context().add_provider(
            css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        python_scroll.set_child(self._python_view)
        python_frame.set_child(python_scroll)
        self._python_revealer.set_child(python_frame)
        editor_box.append(self._python_revealer)

        editor_frame.set_child(editor_box)
        right_paned.set_start_child(editor_frame)

        # Output-panel med debugger-info
        output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._output = OutputPanel()
        output_box.append(self._output)

        # Debugger-variabler (dold som standard)
        self._debug_revealer = Gtk.Revealer()
        self._debug_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_UP
        )
        debug_frame = Gtk.Frame(label="Variabler")
        self._variables_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._variables_box.set_margin_start(8)
        self._variables_box.set_margin_end(8)
        self._variables_box.set_margin_top(4)
        self._variables_box.set_margin_bottom(4)
        debug_frame.set_child(self._variables_box)
        self._debug_revealer.set_child(debug_frame)
        output_box.append(self._debug_revealer)

        right_paned.set_end_child(output_box)
        right_paned.set_position(400)

        self._main_paned.set_end_child(right_paned)
        self._main_paned.set_position(320)

        main_box.append(self._main_paned)

        # Statusfält
        self._statusbar = Gtk.Label(
            label="Redo att programmera!"
        )
        self._statusbar.set_halign(Gtk.Align.START)
        self._statusbar.set_margin_start(12)
        self._statusbar.set_margin_top(4)
        self._statusbar.set_margin_bottom(4)
        self._statusbar.add_css_class("dim-label")
        main_box.append(self._statusbar)

        self.set_content(main_box)

        # Tangentbordsgenvägar
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

        # Realtidsöversättning
        self._editor.get_buffer().connect("changed", self._on_code_changed)

    def _build_tutorial_panel(self) -> Gtk.Box:
        """Bygg tutorial-sidopanelen."""
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel.set_size_request(300, -1)

        # Tutorial-rubrik
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        header_box.set_margin_top(8)
        header_box.set_margin_bottom(4)

        header_label = Gtk.Label(label="Lektioner")
        header_label.add_css_class("title-3")
        header_box.append(header_label)
        panel.append(header_box)

        # Tutorial-lista
        self._tutorial_stack = Gtk.Stack()
        self._tutorial_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )

        # Listvy med tutorials
        list_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        list_scroll = Gtk.ScrolledWindow()
        list_scroll.set_vexpand(True)

        self._tutorial_listbox = Gtk.ListBox()
        self._tutorial_listbox.set_selection_mode(
            Gtk.SelectionMode.SINGLE
        )
        self._tutorial_listbox.add_css_class("boxed-list")
        self._tutorial_listbox.set_margin_start(8)
        self._tutorial_listbox.set_margin_end(8)
        self._tutorial_listbox.connect(
            "row-activated", self._on_tutorial_selected
        )

        for tutorial in self._tutorial_manager.get_all():
            row = Adw.ActionRow(
                title=tutorial.title,
                subtitle=tutorial.description,
            )
            row.set_activatable(True)
            row.tutorial_id = tutorial.id
            self._tutorial_listbox.append(row)

        list_scroll.set_child(self._tutorial_listbox)
        list_page.append(list_scroll)
        self._tutorial_stack.add_named(list_page, "list")

        # Detaljvy
        detail_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Tillbaka-knapp
        back_btn = Gtk.Button(icon_name="go-previous-symbolic")
        back_btn.set_halign(Gtk.Align.START)
        back_btn.set_margin_start(8)
        back_btn.set_margin_top(4)
        back_btn.connect(
            "clicked",
            lambda _: self._tutorial_stack.set_visible_child_name("list"),
        )
        detail_page.append(back_btn)

        detail_scroll = Gtk.ScrolledWindow()
        detail_scroll.set_vexpand(True)

        self._detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._detail_box.set_margin_start(12)
        self._detail_box.set_margin_end(12)
        self._detail_box.set_margin_top(8)
        self._detail_box.set_spacing(8)

        self._tutorial_title = Gtk.Label()
        self._tutorial_title.add_css_class("title-2")
        self._tutorial_title.set_halign(Gtk.Align.START)
        self._tutorial_title.set_wrap(True)
        self._detail_box.append(self._tutorial_title)

        self._step_label = Gtk.Label()
        self._step_label.set_halign(Gtk.Align.START)
        self._step_label.set_wrap(True)
        self._step_label.set_use_markup(True)
        self._step_label.set_selectable(True)
        self._detail_box.append(self._step_label)

        # Kodexempel-knapp
        self._hint_button = Gtk.Button(label="Visa kodexempel")
        self._hint_button.connect("clicked", self._on_hint_clicked)
        self._detail_box.append(self._hint_button)

        # Förklaring (dold tills koden körs)
        self._explanation_revealer = Gtk.Revealer()
        self._explanation_label = Gtk.Label()
        self._explanation_label.set_halign(Gtk.Align.START)
        self._explanation_label.set_wrap(True)
        self._explanation_label.set_use_markup(True)
        self._explanation_label.add_css_class("dim-label")
        self._explanation_revealer.set_child(self._explanation_label)
        self._detail_box.append(self._explanation_revealer)

        # Navigeringsknappar
        nav_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=8
        )
        nav_box.set_margin_top(12)

        self._prev_step_btn = Gtk.Button(label=_("Previous"))
        self._prev_step_btn.connect("clicked", self._on_prev_step)
        nav_box.append(self._prev_step_btn)

        self._next_step_btn = Gtk.Button(label=_("Next page"))
        self._next_step_btn.add_css_class("suggested-action")
        self._next_step_btn.connect("clicked", self._on_next_step)
        nav_box.append(self._next_step_btn)

        self._detail_box.append(nav_box)

        # Utmaning-sektion
        self._challenge_revealer = Gtk.Revealer()
        challenge_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=4
        )
        challenge_box.set_margin_top(12)

        challenge_header = Gtk.Label(label="Utmaning!")
        challenge_header.add_css_class("title-4")
        challenge_header.set_halign(Gtk.Align.START)
        challenge_box.append(challenge_header)

        self._challenge_label = Gtk.Label()
        self._challenge_label.set_halign(Gtk.Align.START)
        self._challenge_label.set_wrap(True)
        challenge_box.append(self._challenge_label)

        self._check_button = Gtk.Button(label="Kontrollera")
        self._check_button.add_css_class("suggested-action")
        self._check_button.connect("clicked", self._on_check_challenge)
        challenge_box.append(self._check_button)

        self._challenge_revealer.set_child(challenge_box)
        self._detail_box.append(self._challenge_revealer)

        detail_scroll.set_child(self._detail_box)
        detail_page.append(detail_scroll)

        self._tutorial_stack.add_named(detail_page, "detail")

        panel.append(self._tutorial_stack)
        return panel

    def _load_tutorial(self, tutorial):
        """Ladda en tutorial och visa första steget."""
        self._current_tutorial = tutorial
        self._current_step = 0
        self._tutorial_title.set_text(tutorial.title)
        self._update_step_display()
        self._tutorial_stack.set_visible_child_name("detail")

    def _update_step_display(self):
        """Uppdatera visningen av aktuellt steg."""
        if not self._current_tutorial:
            return

        steps = self._current_tutorial.steps
        challenges = self._current_tutorial.challenges

        if self._current_step < len(steps):
            step = steps[self._current_step]
            step_num = self._current_step + 1
            total = len(steps)
            self._step_label.set_markup(
                f"<b>Steg {step_num}/{total}</b>\n\n{step.instruction}"
            )
            self._explanation_label.set_markup(step.explanation)
            self._explanation_revealer.set_reveal_child(False)
            self._challenge_revealer.set_reveal_child(False)
            self._hint_button.set_visible(bool(step.code_hint))
        elif challenges:
            # Visa utmaning
            idx = self._current_step - len(steps)
            if idx < len(challenges):
                challenge = challenges[idx]
                self._step_label.set_markup(
                    "<b>Alla steg klara!</b>\nDags för en utmaning:"
                )
                self._challenge_label.set_text(challenge.prompt)
                self._challenge_revealer.set_reveal_child(True)
                self._hint_button.set_visible(bool(challenge.hint))

        # Uppdatera navigeringsknappar
        self._prev_step_btn.set_sensitive(self._current_step > 0)
        total_items = len(steps) + len(challenges)
        self._next_step_btn.set_sensitive(
            self._current_step < total_items - 1
        )

    def _on_tutorial_selected(self, listbox, row):
        """Hantera val av tutorial."""
        tutorial_id = row.tutorial_id
        tutorial = self._tutorial_manager.get_by_id(tutorial_id)
        if tutorial:
            self._load_tutorial(tutorial)

    def _on_hint_clicked(self, _button):
        """Visa kodexempel i editorn."""
        if not self._current_tutorial:
            return

        steps = self._current_tutorial.steps
        if self._current_step < len(steps):
            hint = steps[self._current_step].code_hint
        else:
            idx = self._current_step - len(steps)
            challenges = self._current_tutorial.challenges
            if idx < len(challenges):
                hint = challenges[idx].hint
            else:
                return

        if hint:
            self._editor.set_text(hint)

    def _on_prev_step(self, _button):
        """Gå till föregående steg."""
        if self._current_step > 0:
            self._current_step -= 1
            self._update_step_display()

    def _on_next_step(self, _button):
        """Gå till nästa steg."""
        if self._current_tutorial:
            total = (
                len(self._current_tutorial.steps)
                + len(self._current_tutorial.challenges)
            )
            if self._current_step < total - 1:
                self._current_step += 1
                self._update_step_display()

    def _on_check_challenge(self, _button):
        """Kontrollera utmaningen."""
        self._on_run_clicked(None)

    def _on_run_clicked(self, _button):
        """Kör den svenska koden."""
        swedish_code = self._editor.get_text()
        if not swedish_code.strip():
            self._output.clear()
            self._output.append_info("Skriv lite kod först!\n")
            return

        self._statusbar.set_text("Kör programmet...")
        self._output.clear()

        # Översätt
        result = self._translator.translate(swedish_code)
        if result.errors:
            for error in result.errors:
                self._output.append_stderr(f"Översättningsfel: {error}\n")
            return

        # Kör
        self._run_button.set_sensitive(False)
        self._runner.execute(
            result.python_source,
            callback=lambda r: GLib.idle_add(
                self._on_execution_complete, r
            ),
        )

    def _on_execution_complete(self, result):
        """Hantera resultatet av kodkörning."""
        self._run_button.set_sensitive(True)

        if result.stdout:
            self._output.append_stdout(result.stdout)

        if result.stderr:
            translated_error = self._translator.translate_error(
                result.stderr
            )
            self._output.append_stderr(translated_error + "\n")

        if result.timed_out:
            self._statusbar.set_text("Tidsgräns överskriden!")
        elif result.return_code == 0:
            time_str = f"{result.execution_time_ms:.0f}"
            self._statusbar.set_text(
                f"Klart! ({time_str} ms)"
            )
            self._explanation_revealer.set_reveal_child(True)

            # Kontrollera tutorial-steg
            self._check_tutorial_step(result.stdout)
        else:
            self._statusbar.set_text("Fel vid körning")

        return False  # Ta bort från idle

    def _check_tutorial_step(self, output: str):
        """Kontrollera om tutorial-steget är uppfyllt."""
        if not self._current_tutorial:
            return

        steps = self._current_tutorial.steps
        if self._current_step < len(steps):
            step = steps[self._current_step]
            if self._tutorial_manager.check_output(step, output):
                self._output.append_success("\nBra jobbat! Rätt svar!\n")
        else:
            idx = self._current_step - len(steps)
            challenges = self._current_tutorial.challenges
            if idx < len(challenges):
                challenge = challenges[idx]
                if self._tutorial_manager.validate_challenge(
                    challenge, output
                ):
                    self._output.append_success(
                        "\nUtmärkt! Du klarade utmaningen!\n"
                    )

    def _on_debug_clicked(self, _button):
        """Starta debuggern."""
        swedish_code = self._editor.get_text()
        if not swedish_code.strip():
            return

        self._output.clear()
        self._output.append_info("Debugger startad...\n")

        # Översätt
        result = self._translator.translate(swedish_code)
        if result.errors:
            for error in result.errors:
                self._output.append_stderr(f"Översättningsfel: {error}\n")
            return

        # Starta debugger
        self._debugger.prepare(result.python_source)
        self._debug_revealer.set_reveal_child(True)

        frame = self._debugger.step()
        if frame:
            self._update_debug_display(frame)

        if self._debugger.is_finished():
            self._output.append_info("Debugging klar.\n")
            self._debug_revealer.set_reveal_child(False)

    def _update_debug_display(self, frame):
        """Uppdatera debugger-visningen."""
        # Visa output
        if frame.output:
            self._output.append_stdout(frame.output)

        # Visa variabler
        # Rensa befintliga
        child = self._variables_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._variables_box.remove(child)
            child = next_child

        for name, value in frame.variables.items():
            row = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=8
            )
            name_label = Gtk.Label(label=f"{name}:")
            name_label.add_css_class("heading")
            row.append(name_label)

            value_label = Gtk.Label(label=str(value))
            value_label.set_selectable(True)
            row.append(value_label)

            self._variables_box.append(row)

        # Markera rad
        self._editor.highlight_line(frame.line_number)

        # Visa felmeddelande
        if self._debugger.debug_info.state == DebugState.ERROR:
            self._output.append_stderr(
                f"Fel: {self._debugger.debug_info.error}\n"
            )

    def _on_clear_clicked(self, _button):
        """Rensa editor och output."""
        self._editor.clear()
        self._output.clear()
        self._debug_revealer.set_reveal_child(False)
        self._statusbar.set_text("Redo att programmera!")

    def _on_show_python_toggled(self, button):
        """Visa/dölj Python-översättning."""
        self._python_revealer.set_reveal_child(button.get_active())
        if button.get_active():
            self._update_python_preview()

    def _on_code_changed(self, _buffer):
        """Uppdatera Python-förhandsgranskning vid kodändringar."""
        if self._show_python_button.get_active():
            self._update_python_preview()

    def _update_python_preview(self):
        """Uppdatera Python-förhandsgranskningen."""
        swedish_code = self._editor.get_text()
        python_code = self._translator.get_realtime_preview(swedish_code)
        self._python_view.get_buffer().set_text(python_code)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Hantera tangentbordsgenvägar."""
        from gi.repository import Gdk

        ctrl = state & Gdk.ModifierType.CONTROL_MASK

        if ctrl and keyval == Gdk.KEY_Return:
            self._on_run_clicked(None)
            return True
        if ctrl and keyval == Gdk.KEY_l:
            self._on_clear_clicked(None)
            return True

        return False
