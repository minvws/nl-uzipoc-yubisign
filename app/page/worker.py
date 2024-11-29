import threading
from PyQt6.QtCore import QObject, pyqtSignal
import PyKCS11


class Worker(QObject):
	finished = pyqtSignal()

	def __init__(self, mypkcs, currentStep, selectedYubiKeySlot):
		super().__init__()
		self.pkcs = mypkcs
		self.currentStep = currentStep
		self.selectedYubiKeySlot = selectedYubiKeySlot

	def task(self):
		try:
			print("** Worker", self.currentStep)
			# keysize of 4096 is not supported, for more info:
			# https://github.com/Yubico/yubico-piv-tool/issues/58
			public_template = [
				(PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY),
				(PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
				(PyKCS11.CKA_TOKEN, PyKCS11.CK_TRUE),
				(PyKCS11.CKA_ID, [self.currentStep]),
				(PyKCS11.CKA_MODULUS_BITS, 2048),
				(
					PyKCS11.CKA_PUBLIC_EXPONENT,
					(0x01, 0x00, 0x01),
				),
			]
			private_template = [
				(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
				(PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
				(PyKCS11.CKA_TOKEN, PyKCS11.CK_TRUE),
				(PyKCS11.CKA_ID, [self.currentStep]),
			]
			session = self.pkcs.getadminsession(self.selectedYubiKeySlot)
			print(
				"** Output", session.generateKeyPair(public_template, private_template)
			)
			self.pkcs.delsession(self.selectedYubiKeySlot)
			# print("done")
		except Exception:
			print("Bla")
		finally:
			print("** Worker done", self.currentStep)
			self.finished.emit()

	def run(self):
		thread = threading.Thread(target=self.task)
		thread.start()
