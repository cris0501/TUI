from textual.widget import Widget
from rich.text import Text


class TitleBar(Widget):
    def render(self) -> Text:
        state = self.app.state
        width = self.size.width
        title = state.app_name
        status = state.status
        padding = max(0, width - len(title) - len(status) - 2)
        return Text.assemble(
            (f" {title}", "bold cyan"),
            (" " * padding, ""),
            (f"{status}\n", "bold green"),
            ("─" * width, "white"),
        )
