from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label, Rule
from textual.containers import Horizontal


class PromptBar(Widget):
    def compose(self) -> ComposeResult:
        yield Rule()
        with Horizontal():
            yield Label(">> ", id="prompt_prefix")
            yield Input(id="prompt_input")

    def set_prefix(self, text: str) -> None:
        self.query_one("#prompt_prefix", Label).update(text)

    def focus_input(self) -> None:
        self.query_one(Input).focus()

