TEST_CERT = "-----BEGIN CERTIFICATE-----\ntestcert1\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\ntestcert2\n-----END CERTIFICATE-----\n"


def test_cert_split():
	# Split on the second certificate ending so the first one is the user certificate
	cert1, _ = TEST_CERT.split("\n-----BEGIN CERTIFICATE-----\n")

	assert cert1 == "-----BEGIN CERTIFICATE-----\ntestcert1\n-----END CERTIFICATE-----"
