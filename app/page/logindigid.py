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

from bs4 import BeautifulSoup


class LoginWithDigiDPage(QWizardPage):
	profile = None
	browser = None

	def __init__(self, myacme, parent=None):
		super().__init__(parent)
		# super(LoginWithDigiDPage, self).__init__(parent)
		self.acme = myacme

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

		url = QUrl("https://proeftuin.uzi-online.irealisatie.nl/oidc/login")
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
		if (
			url.toString()
			== "https://proeftuin.uzi-online.irealisatie.nl/ziekenboeg/users/home"
		):
			self.browser.load(
				QUrl("https://proeftuin.uzi-online.irealisatie.nl/ziekenboeg/users/jwt")
			)

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
			if (
				current_url
				== "https://proeftuin.uzi-online.irealisatie.nl/ziekenboeg/users/jwt"
			):
				self.browser.page().toHtml(self.htmlCaptured)
