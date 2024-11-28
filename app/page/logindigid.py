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
    profile = None
    browser = None

    acme: ACME

    _oidc_provider_base_url: urllib.parse.ParseResult

    def __init__(
        self,
        myacme: ACME,
        oidc_provider_base_url: urllib.parse.ParseResult,
        parent=None,
    ):
        super().__init__(parent)
        self.acme = myacme
        self._oidc_provider_base_url = oidc_provider_base_url

    def _get_jwt_url(self):
        return urllib.parse.urljoin(
            self._oidc_provider_base_url.geturl(), "ziekenboeg/users/jwt"
        )

    def initializePage(self):
        layout = QVBoxLayout(self)
        self.profile = QWebEngineProfile("CustomProfile", self)
        self.browser = QWebEngineView()
        self.browser.setPage(QWebEnginePage(self.profile, self.browser))
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

        login_url = urllib.parse.urljoin(
            self._oidc_provider_base_url.geturl(), "/oidc/login"
        )
        url = QUrl(login_url)

        query = QUrlQuery()
        query.addQueryItem(
            "acme_tokens", ",".join(self.acme.tokens)
        )  # Replace with your parameter name and value
        url.setQuery(query)
        self.browser.load(url)

        layout.addWidget(self.browser)

        self.browser.urlChanged.connect(self.onUrlChanged)
        self.browser.loadFinished.connect(self.onLoadFinished)

    def isComplete(self):
        if self.acme.jwt_token:
            return True
        return False

    def onUrlChanged(self, url):
        print(url.toString())

        user_home_url = urllib.parse.urljoin(
            self._oidc_provider_base_url.geturl(), " /ziekenboeg/users/home"
        )
        if url.toString() == user_home_url:
            self.browser.load(QUrl(self._get_jwt_url()))

    def captureHtml(self, ok):
        if ok:
            self.browser.page().toHtml(self.htmlCaptured)

    def htmlCaptured(self, html):
        print(html)
        soup = BeautifulSoup(html, "html.parser")
        pre_tag = soup.find("pre")
        if pre_tag:
            self.acme.jwt_token = pre_tag.get_text()
            self.wizard().setProperty("jwt_token", self.acme.gettoken)
            print("Got JWT:", self.acme.gettoken())
            self.wizard().next()

    def onLoadFinished(self, ok):
        if ok:
            current_url = self.browser.url().toString()
            if current_url == self._get_jwt_url():
                self.browser.page().toHtml(self.htmlCaptured)
