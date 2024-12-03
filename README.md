# PoC with Yubikey

In order to automate certificate issuance for UZI, a PoC was done with a YubiKey(an hardware token) and an ACME server. The keypairs are generated on the YubiKey and the certificate is issued by the ACME server. This document will give you an high overview.

### Steps

- The YubiKey is reset: all the certificates on the device will be removed.
- We will generate 4 public and private key pairs on the YubiKey. These are for PIV Authentication, Digital Signature, Key Management and Card Authentication. Next to that, the YubiKey will generate additional attestation certificates, to prove that the private key is generated on the YubiKey itself. The private keys will always remain in the YubiKey.
- The user logs in via the chosen [authentication flow](./AUTH_FLOW.md). This returns an JWT, containing the user information.
- Per generated key pair, an certificate signing request (CSR) is created and signed by the private key.
- Finally, each certificate signing request with the corresponding attestation certificate is validated at the ACME server. When this is done, the server will issue an certificate for every key pair. Here, the JWT of the user is also used. This is done with a [fork of letsencrypt-boulder](https://github.com/minvws/letsencrypt-boulder). These are then saved back into the YubiKey into the corresponding slot.

Now it is possible to use the certificate on the YubiKey to sign data.

#### Diagram flow

This diagram expecst that the key is already plugged in the user's computer.

```mermaid
sequenceDiagram
    actor APP
    participant YUBIKEY

    APP->>YUBIKEY: 1. Sends request to empty the Yubikeys certificates
    YUBIKEY-->YUBIKEY: Empties the certificates

    APP->>YUBIKEY: 2. Sends request to generate 4 new private key pairs
    YUBIKEY-->YUBIKEY: 2.1 Create key pair for PIV Authentication
    YUBIKEY-->YUBIKEY: 2.2 Create key pair for Digital Signature
    YUBIKEY-->YUBIKEY: 2.3 Create key pair for Key Management
    YUBIKEY-->YUBIKEY: 2.4 Create key pair for Card Authentication

    create participant MAX
    APP->>MAX: 3. Opens browser to login the user
    MAX-->MAX: 3.1 Validates the user
    MAX-->>APP: Returns the JWT containing the user information.

    APP->>APP: 4. Per generated key pair, <br> an certificate signing request (CSR)<br> is created and signed by the private key.

    create participant BOULDER_FORK
    loop 5. For every certificate signing request (CSR)
        APP->>BOULDER_FORK: Validate every certificate signing request with the corresponding attestation certificate
        BOULDER_FORK-->>APP: OK
    end

    loop 6. For every key pair
        APP->>BOULDER_FORK: Request certificate for every key pair, also using the users' JWT
        BOULDER_FORK-->>APP: OK
        BOULDER_FORK-->>YUBIKEY: Save certificates
    end

```

### Disclaimer

This Repository is created as a PoC (Proof of Concept) as part of the project _Toekomstbestendig maken UZI_, and
**should not be used as is in any production environment**.

### Licentie

This project is licensed under the [EUPL-1.2 license](./LICENSE.txt).
