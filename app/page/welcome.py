import pathlib
from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QTextBrowser


class WelcomePage(QWizardPage):
    _TITLE = "Welcome"
    _HTML_FILE = pathlib.Path(__file__).parent / "welcome.html"

    def _read_html_content(self):
        with open(self._HTML_FILE, "r") as file:
            return file.read()

    def _setup_ui(self):
        self.setTitle(self._TITLE)

        layout = QVBoxLayout(self)

        content = self._read_html_content()

        htmlView = QTextBrowser()
        htmlView.setHtml(content)
        htmlView.setStyleSheet("background: transparent")
        layout.addWidget(htmlView)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
