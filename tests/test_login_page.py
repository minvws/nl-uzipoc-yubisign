from typing import Optional
from unittest.mock import MagicMock
from urllib.parse import urlparse
from pytestqt.qtbot import QtBot

from app.page.logindigid import LoginWithDigiDPage


class AcmeMock(MagicMock):
    jwt_token: Optional[str]
    tokens: list[str] = []

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.jwt_token = None

    def getchallenge(self, x):
        self.tokens = ["1", "2", "3", "4"]


def test_login_sample_load(qtbot: QtBot):
    acme = AcmeMock()
    oidc_provider_base_url = urlparse("https://127.0.0.1/")

    page = LoginWithDigiDPage(acme, oidc_provider_base_url)
    qtbot.addWidget(page)

    with qtbot.wait_signal(page.browser.loadFinished):
        ...

    actualurl = page.browser.url().toString()
    assert actualurl == "https://127.0.0.1/oidc/login?acme_tokens=1,2,3,4"
    assert page.isComplete() is False


def test_html_capture(qtbot: QtBot):
    acme = AcmeMock()
    oidc_provider_base_url = urlparse("https://127.0.0.1/")

    page = LoginWithDigiDPage(acme, oidc_provider_base_url)
    qtbot.addWidget(page)

    with qtbot.wait_signal(page.browser.loadFinished):
        ...

    actualurl = page.browser.url().toString()
    assert actualurl == "https://127.0.0.1/oidc/login?acme_tokens=1,2,3,4"
    assert page.isComplete() is False
