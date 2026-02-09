from textual.widgets import RichLog
import textual.widgets._rich_log

textlog = RichLog()


def get_textlog() -> textual.widgets._rich_log.RichLog:
    return textlog
