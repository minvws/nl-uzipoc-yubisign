from PyQt6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
)
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QUrlQuery
from ..appacme import ACME

from bs4 import BeautifulSoup

import urllib.parse


class LoginWithDigiDPage(QWizardPage):
    browser: QWebEngineView
    acme: ACME

    _oidc_provider_base_url: urllib.parse.ParseResult

    @property
    def _current_browser_url(self) -> str:
        return self.browser.url().toString()

    def __init__(
        self,
        myacme: ACME,
        oidc_provider_base_url: urllib.parse.ParseResult,
        parent=None,
    ):
        super().__init__(parent)
        self.acme = myacme
        self._oidc_provider_base_url = oidc_provider_base_url

        self._prepare_acme_object()
        self._setup_ui()

    def _get_jwt_url(self):
        return urllib.parse.urljoin(self._oidc_provider_base_url.geturl(), "ziekenboeg/users/jwt")

    def _build_browser(self) -> QWebEngineView:
        profile = QWebEngineProfile("CustomProfile", self)
        browser = QWebEngineView()

        page = QWebEnginePage(profile, browser)
        browser.setPage(page)

        query = QUrlQuery()
        query.addQueryItem("acme_tokens", ",".join(self.acme.tokens))

        login_url = urllib.parse.urljoin(self._oidc_provider_base_url.geturl(), "oidc/login")
        url = QUrl(login_url)
        url.setQuery(query)

        browser.load(url)

        browser.urlChanged.connect(self.onUrlChanged)
        browser.loadFinished.connect(self.onLoadFinished)

        return browser

    def _prepare_acme_object(self):
        self.acme.challenges = [{}, {}, {}, {}]
        self.acme.tokens = ["", "", "", ""]

        # First, based on every PIV-slot of the Yubikey an order is created.
        # This will return a challenge url.
        #
        # This URL is fetched, returning a random token. Further in the process, this token (per PIV-slot)
        # is then saved back into the users' JWT. This is due to that the token is given in the params of the OIDC provider
        for keynum in [1, 2, 3, 4]:
            self.acme.order(keynum)
            self.acme.getchallenge(keynum - 1)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.browser = self._build_browser()
        layout.addWidget(self.browser)

    def isComplete(self):
        return bool(self.acme.jwt_token)

    def onUrlChanged(self, url: QUrl):
        # This method will also get called on the intial page load. We only need this to load the JWT
        # page when the user navigates to the /home page
        user_home_url = urllib.parse.urljoin(self._oidc_provider_base_url.geturl(), "ziekenboeg/users/home")
        if url.toString() == user_home_url:
            self.browser.load(QUrl(self._get_jwt_url()))

    def captureHtml(self, ok):
        if ok:
            self.browser.page().toHtml(self.htmlCaptured)

    def htmlCaptured(self, html: str):
        print(html)
        soup = BeautifulSoup(html, "html.parser")
        pre_tag = soup.find("pre")
        if pre_tag:
            self.acme.jwt_token = pre_tag.get_text()
            self.wizard().setProperty("jwt_token", self.acme.gettoken)
            print("Got JWT:", self.acme.gettoken())
            self.wizard().next()

    def onLoadFinished(self, ok: bool):
        current_url = self._current_browser_url

        if ok:
            if current_url == self._get_jwt_url():
                self.browser.page().toHtml(self.htmlCaptured)
