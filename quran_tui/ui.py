from __future__ import annotations

from prompt_toolkit.application import Application
from prompt_toolkit.filters import Condition, has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ConditionalContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from .models import Ayah, QuranData, SurahData
from .rtl import reshape_arabic
from .search import QuranSearchEngine, SearchResult
from .state import ReadingState, ReadingStateStore


class QuranTUIApplication:
    """Main full-screen Quran terminal UI."""

    def __init__(
        self,
        quran_data: QuranData,
        search_engine: QuranSearchEngine,
        state_store: ReadingStateStore,
        *,
        enable_color: bool = True,
    ) -> None:
        self.quran_data = quran_data
        self.search_engine = search_engine
        self.state_store = state_store

        self.mode = "browse"
        self.search_results: list[SearchResult] = []
        self.search_index = 0
        self.last_query = ""
        self.message = "Ready."

        self.prompt_visible = False
        self.prompt_kind = "search"

        self.surah_control = FormattedTextControl(self._render_surahs, focusable=True)
        self.main_control = FormattedTextControl(self._render_main, focusable=True)
        self.header_control = FormattedTextControl(self._render_header)
        self.status_control = FormattedTextControl(self._render_status)

        self.surah_window = Window(content=self.surah_control, wrap_lines=False, always_hide_cursor=True)
        self.main_window = Window(content=self.main_control, wrap_lines=True, always_hide_cursor=True)
        self.prompt_input = TextArea(
            multiline=False,
            wrap_lines=False,
            height=1,
            prompt="Search> ",
            style="class:prompt",
        )

        loaded_state = self.state_store.load()
        self.current_surah_index = self._clamp(loaded_state.surah_number - 1, 0, len(self.quran_data.surahs) - 1)
        self.current_ayah_index = 0
        self._set_current_ayah_index(loaded_state.ayah_number - 1)

        root = HSplit(
            [
                Window(content=self.header_control, height=1, style="class:header"),
                VSplit(
                    [
                        Frame(
                            self.surah_window,
                            title="Surahs",
                            width=Dimension(weight=35),
                        ),
                        Frame(
                            self.main_window,
                            title="Mushaf / Search",
                            width=Dimension(weight=65),
                        ),
                    ],
                    padding=1,
                ),
                Window(content=self.status_control, height=1, style="class:status"),
                ConditionalContainer(
                    content=Frame(self.prompt_input, title="Command"),
                    filter=Condition(lambda: self.prompt_visible),
                ),
            ]
        )

        self.app = Application(
            layout=Layout(root, focused_element=self.main_window),
            key_bindings=self._build_key_bindings(),
            full_screen=True,
            style=self._build_style(enable_color=enable_color),
            mouse_support=False,
        )

    def run(self) -> None:
        self.app.run()

    def _build_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("q")
        @kb.add("c-c")
        def _quit(event) -> None:
            event.app.exit()

        @kb.add("tab", filter=~has_focus(self.prompt_input))
        def _toggle_focus(event) -> None:
            current_control = event.app.layout.current_control
            if current_control == self.surah_control:
                event.app.layout.focus(self.main_window)
            else:
                event.app.layout.focus(self.surah_window)

        @kb.add("left", filter=~has_focus(self.prompt_input))
        def _focus_surahs(event) -> None:
            event.app.layout.focus(self.surah_window)

        @kb.add("right", filter=~has_focus(self.prompt_input))
        def _focus_main(event) -> None:
            event.app.layout.focus(self.main_window)

        @kb.add("up", filter=~has_focus(self.prompt_input))
        @kb.add("k", filter=~has_focus(self.prompt_input))
        def _move_up(event) -> None:
            if event.app.layout.current_control == self.surah_control:
                self._move_surah(-1)
                return
            if self.mode == "search":
                self._move_search_cursor(-1)
            else:
                self._move_ayah(-1)

        @kb.add("down", filter=~has_focus(self.prompt_input))
        @kb.add("j", filter=~has_focus(self.prompt_input))
        def _move_down(event) -> None:
            if event.app.layout.current_control == self.surah_control:
                self._move_surah(1)
                return
            if self.mode == "search":
                self._move_search_cursor(1)
            else:
                self._move_ayah(1)

        @kb.add("n", filter=~has_focus(self.prompt_input))
        def _next_surah(event) -> None:
            self._move_surah(1)

        @kb.add("p", filter=~has_focus(self.prompt_input))
        def _prev_surah(event) -> None:
            self._move_surah(-1)

        @kb.add("b", filter=~has_focus(self.prompt_input))
        def _back_to_browse(event) -> None:
            self.mode = "browse"
            self.message = "Browse mode."

        @kb.add("/", filter=~has_focus(self.prompt_input))
        def _open_search(event) -> None:
            self._open_prompt(event, "search")

        @kb.add("g", filter=~has_focus(self.prompt_input))
        def _open_jump(event) -> None:
            self._open_prompt(event, "jump")

        @kb.add("r", filter=~has_focus(self.prompt_input))
        def _resume(event) -> None:
            self._resume_from_saved_state()

        @kb.add("enter", filter=~has_focus(self.prompt_input))
        def _enter(event) -> None:
            if self.mode == "search" and event.app.layout.current_control == self.main_control:
                self._open_selected_search_result()
            elif event.app.layout.current_control == self.surah_control:
                event.app.layout.focus(self.main_window)

        @kb.add("escape", filter=has_focus(self.prompt_input))
        def _cancel_prompt(event) -> None:
            self._close_prompt(event, "Cancelled.")

        @kb.add("enter", filter=has_focus(self.prompt_input))
        def _submit_prompt(event) -> None:
            self._submit_prompt(event)

        return kb

    def _open_prompt(self, event, prompt_kind: str) -> None:
        self.prompt_visible = True
        self.prompt_kind = prompt_kind
        self.prompt_input.text = ""
        self.prompt_input.prompt = "Search> " if prompt_kind == "search" else "Surah #> "
        event.app.layout.focus(self.prompt_input)
        self.message = "Type and press Enter."

    def _close_prompt(self, event, message: str) -> None:
        self.prompt_visible = False
        self.prompt_input.text = ""
        self.message = message
        event.app.layout.focus(self.main_window)

    def _submit_prompt(self, event) -> None:
        raw = self.prompt_input.text.strip()
        prompt_kind = self.prompt_kind
        self.prompt_visible = False
        self.prompt_input.text = ""
        event.app.layout.focus(self.main_window)

        if prompt_kind == "search":
            self._run_search(raw)
            return
        self._jump_to_surah(raw)

    def _run_search(self, query: str) -> None:
        self.last_query = query
        if not query:
            self.message = "Search text is empty."
            return

        self.search_results = self.search_engine.search(query)
        if not self.search_results:
            self.mode = "browse"
            self.message = f"No result for: {query}"
            return

        self.mode = "search"
        self.search_index = 0
        self.message = f"{len(self.search_results)} results for: {query}"

    def _open_selected_search_result(self) -> None:
        if not self.search_results:
            self.message = "No result selected."
            return

        selected = self.search_results[self.search_index]
        self.current_surah_index = self._clamp(selected.ayah.surah_number - 1, 0, len(self.quran_data.surahs) - 1)
        self._set_current_ayah_index(selected.ayah.ayah_number - 1)
        self.mode = "browse"
        self.message = f"Jumped to {selected.ayah.surah_number}:{selected.ayah.ayah_number}"
        self._save_state()

    def _jump_to_surah(self, raw_value: str) -> None:
        if not raw_value:
            self.message = "Type a number from 1 to 114."
            return

        try:
            surah_number = int(raw_value)
        except ValueError:
            self.message = "Surah must be a number."
            return

        if not (1 <= surah_number <= len(self.quran_data.surahs)):
            self.message = f"Range is 1 to {len(self.quran_data.surahs)}."
            return

        self.current_surah_index = surah_number - 1
        self.current_ayah_index = 0
        self.mode = "browse"
        self.message = f"Opened surah {surah_number}."
        self._save_state()

    def _resume_from_saved_state(self) -> None:
        state = self.state_store.load()
        self.current_surah_index = self._clamp(state.surah_number - 1, 0, len(self.quran_data.surahs) - 1)
        self._set_current_ayah_index(state.ayah_number - 1)
        self.mode = "browse"
        self.message = f"Resumed at {self.current_surah.number}:{self.current_ayah.ayah_number}"

    def _move_surah(self, step: int) -> None:
        old_index = self.current_surah_index
        self.current_surah_index = self._clamp(old_index + step, 0, len(self.quran_data.surahs) - 1)
        if self.current_surah_index == old_index:
            return

        self.current_ayah_index = 0
        self.mode = "browse"
        self.message = f"Surah {self.current_surah.number}: {self.current_surah.name_english}"
        self._save_state()

    def _move_ayah(self, step: int) -> None:
        old_index = self.current_ayah_index
        self._set_current_ayah_index(old_index + step)
        if self.current_ayah_index == old_index:
            return

        self.mode = "browse"
        self.message = f"Ayah {self.current_surah.number}:{self.current_ayah.ayah_number}"
        self._save_state()

    def _move_search_cursor(self, step: int) -> None:
        if not self.search_results:
            return
        self.search_index = self._clamp(self.search_index + step, 0, len(self.search_results) - 1)
        selected = self.search_results[self.search_index]
        self.message = f"Selected {selected.ayah.surah_number}:{selected.ayah.ayah_number}"

    def _set_current_ayah_index(self, new_index: int) -> None:
        max_ayah_index = max(0, len(self.current_surah.ayahs) - 1)
        self.current_ayah_index = self._clamp(new_index, 0, max_ayah_index)

    def _save_state(self) -> None:
        self.state_store.save(
            ReadingState(
                surah_number=self.current_surah.number,
                ayah_number=self.current_ayah.ayah_number,
            )
        )

    @property
    def current_surah(self) -> SurahData:
        return self.quran_data.surahs[self.current_surah_index]

    @property
    def current_ayah(self) -> Ayah:
        return self.current_surah.ayahs[self.current_ayah_index]

    def _render_header(self):
        return [
            ("class:header", " Quran TUI | browse surahs | fuzzy verse search | resume reading "),
        ]

    def _render_status(self):
        focus_name = "Surahs" if self._focus_is_surah() else "Reader"
        if self.prompt_visible:
            focus_name = "Command"
        location = f"{self.current_surah.number}:{self.current_ayah.ayah_number}"
        help_text = " ↑↓/jk move  tab switch  / search  g jump  enter open  b browse  r resume  q quit "
        text = f" {focus_name} | {location} | {self.message} |{help_text}"
        return [("class:status", text)]

    def _render_surahs(self):
        surahs = self.quran_data.surahs
        start = max(0, self.current_surah_index - 11)
        end = min(len(surahs), start + 24)
        start = max(0, end - 24)

        output: list[tuple[str, str]] = []
        if start > 0:
            output.append(("class:muted", " ...\n"))

        surah_focus = self._focus_is_surah()
        for index in range(start, end):
            surah = surahs[index]
            is_active = index == self.current_surah_index
            marker = ">" if is_active else " "
            style = "class:active"
            if is_active and not surah_focus:
                style = "class:active-soft"
            if not is_active:
                style = "class:surah"

            line = f"{marker} {surah.number:>3}. {surah.name_english}\n"
            output.append((style, line))

        if end < len(surahs):
            output.append(("class:muted", " ...\n"))

        return output

    def _render_main(self):
        if self.mode == "search":
            return self._render_search_results()
        return self._render_mushaf_view()

    def _render_mushaf_view(self):
        surah = self.current_surah
        ayahs = surah.ayahs

        output: list[tuple[str, str]] = []
        output.append(
            (
                "class:title",
                f"Surah {surah.number} - {surah.name_english}\n",
            )
        )
        output.append(
            (
                "class:title",
                f"{reshape_arabic(surah.name_arabic)}\n",
            )
        )

        if surah.bismillah_pre:
            bismillah_ar = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"
            bismillah_en = "In the name of Allah, the Most Gracious, the Most Merciful"
            output.append(("class:muted", f"\n{reshape_arabic(bismillah_ar)}\n"))
            output.append(("class:muted", f"{bismillah_en}\n"))

        output.append(("", "\n"))

        visible_count = 7
        half = visible_count // 2
        start = max(0, self.current_ayah_index - half)
        end = min(len(ayahs), start + visible_count)
        if end == len(ayahs):
            start = max(0, end - visible_count)

        if start > 0:
            output.append(("class:muted", f"  ↑ {start} more verse(s) above\n\n"))

        main_focus = self._focus_is_main()
        for index in range(start, end):
            ayah = ayahs[index]
            is_active = index == self.current_ayah_index
            marker = "▶" if is_active else " "

            arabic_style = "class:ayah"
            english_style = "class:translation"
            if is_active:
                if main_focus:
                    arabic_style = "class:active-ayah"
                    english_style = "class:active-translation"
                else:
                    arabic_style = "class:active-ayah-soft"
                    english_style = "class:active-translation-soft"

            arabic_text = reshape_arabic(ayah.text_arabic)
            ayah_mark = f" ﴿{ayah.ayah_number}﴾"
            output.append((arabic_style, f"{arabic_text}{ayah_mark}\n"))
            output.append((english_style, f"{marker} {ayah.ayah_number}. {ayah.text_english}\n\n"))

        if end < len(ayahs):
            remaining = len(ayahs) - end
            output.append(("class:muted", f"  ↓ {remaining} more verse(s) below\n"))
        else:
            output.append(("class:muted", "─" * 40 + "\n"))
            output.append(("class:muted", f"۝ End of Surah {surah.name_english} ۝\n"))

        return output

    def _render_search_results(self):
        output: list[tuple[str, str]] = []
        header = f"Search: {self.last_query!r} ({len(self.search_results)} results)\n\n"
        output.append(("class:title", header))

        if not self.search_results:
            output.append(("class:muted", "No results.\n"))
            return output

        for index, result in enumerate(self.search_results):
            ayah = result.ayah
            is_active = index == self.search_index
            marker = ">" if is_active else " "
            style = "class:result-active" if is_active else "class:result"
            snippet_style = "class:result-active-snippet" if is_active else "class:translation"
            line = f"{marker} {ayah.surah_number}:{ayah.ayah_number} {ayah.surah_name_english}  (score {result.score:.1f})\n"
            output.append((style, line))
            output.append((snippet_style, f"    {result.preview}\n\n"))

        output.append(("class:muted", "Press Enter to open highlighted ayah, or b to go back.\n"))
        return output

    def _focus_is_surah(self) -> bool:
        try:
            return self.app.layout.current_control == self.surah_control
        except Exception:
            return False

    def _focus_is_main(self) -> bool:
        try:
            return self.app.layout.current_control == self.main_control
        except Exception:
            return False

    def _build_style(self, *, enable_color: bool) -> Style:
        if not enable_color:
            return Style.from_dict({})

        return Style.from_dict(
            {
                "header": "reverse bold",
                "status": "reverse",
                "title": "bold",
                "muted": "#777777",
                "surah": "#d9d9d9",
                "active": "bg:#1f4f99 #ffffff bold",
                "active-soft": "bg:#3d4f6b #ffffff",
                "ayah": "#f2f2f2",
                "translation": "#9ea4ad",
                "active-ayah": "bg:#0f5c4b #ffffff bold",
                "active-translation": "bg:#0f5c4b #e2efe9",
                "active-ayah-soft": "bg:#2f4f4f #ffffff",
                "active-translation-soft": "bg:#2f4f4f #d9e4df",
                "result": "#e4e4e4",
                "result-active": "bg:#5f2a5f #ffffff bold",
                "result-active-snippet": "bg:#5f2a5f #f0e7f0",
                "prompt": "bg:#202020 #f0f0f0",
            }
        )

    @staticmethod
    def _clamp(value: int, low: int, high: int) -> int:
        return max(low, min(value, high))
