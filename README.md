# Wat doet dit?

Dit neemt een yubikey (doe maar versie 5) en maakt daarin de PIV module *leeg*

Nadat deze leeg is worden er 4 keys aangemaakt in de yubikey

Er wordt contact gelegd met de rdo-acme service. En er worden 4 orders aangemaakt

Van deze 4 orders wordt de unique-anti-replay-token meegestuurd met een uzi-labs digid login verzoek

Er wordt een browser geopend in de applicatie zelf, daarmee log je in als zorg identiteit bij de ziekenboeg-uzi-labs

De app haalt hierna de JWT-token op bij ziekenboeg-uzi-labs waarin de 4 acmetokens zitten.

Er wordt van de yubikey zelf opgehaald:
* Het intermediate certificaat behorende bij de yubikey zoals geleverd door yubico op de yubikey zelf

Per sleutel op de yubikey:
* Een door de yubikey ondertekend certificaat per sleutel waarin de garantie (attestation) staat dat de sleutel echt op een yubikey is gemaakt
* een CSR verzoek ondertekend door de aangemaakte sleutel

Per order wordt dan verstuurd:
* De JWT
* Het yubikey intermediate certificaat
* Het attestation certificaat

De acme server controleert dan per order:
* of het attestation certificaat van de sleutel klopt
* het token voor order in de JWT zit
* De JWT goed is en van een geldige uzi-cibg-labs-uitgever komt

Als dat klopt dan geeft de acme server terug dat het klopt en dan vraagt deze app in de laatste stap een certificaat aan met de eerder genoemde CSR.

Als de CSR dezelfde public key heeft als in de vorige stap gecontroleerde gegevens wordt er een Labs-UZI certifcaat uitgegeven op basis van de gegevens in de JWT.
Dit certificaat bevat de huidige UZI-Certificaten structuur.

Als er een certificaat is opgehaald wordt dit opgeslagen op de juiste plek in de yubikey.

Door het laden van de yubikey pkcs11 library in de browser, office, mac os, windows of linux plekken (zoals beschreven door yubico) kan de yubikey daarna
worden gebruikt zoals een UZIpas ook gebruikt kan worden. Voor digitaal ondertekenen van documenten, verzoeken en om in te loggen in de browser bij
partijen die UZI certificaten login mogelijk maken.
