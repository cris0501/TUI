from textual.widgets import RichLog


class MainPanel(RichLog):
    DEFAULT_CSS = """
    MainPanel {
        border: none;
        padding: 0 1;
        scrollbar-gutter: stable;
    }
    """

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("highlight", False)
        kwargs.setdefault("markup", False)
        super().__init__(**kwargs)
