from textual.widget import Widget
from rich.text import Text


class FooterBar(Widget):
    def render(self) -> Text:
        state = self.app.state
        width = self.size.width

        sys_parts = [f"{k}: {v}" for k, v in state.system_actions.items()]
        sys_parts.append("F9: Exit")
        sys_str = " | ".join(sys_parts)

        opts = " | ".join(f"{k}: {v}" for k, v in state.actions.items())
        padding = max(1, width - len(opts) - len(sys_str) - 2)

        return Text.assemble(
            (f" {opts}", "dim"),
            (" " * padding, ""),
            (f"{sys_str} ", "bold magenta"),
        )
