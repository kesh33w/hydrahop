# Security

Report suspected vulnerabilities privately, using GitHub's **Report a vulnerability** button on the Security tab, not in a public issue.

- **The Internet Link uses mutual TLS.** Enrollment issues a client certificate from a CA whose key stays on the Pi (`/etc/openhop_repeater/private-link/`). Data never flows without mTLS.
- **Never commit** any of the following; they are installation inputs:
  - CA or issuer keys, client certificates, enrollment records;
  - Wi-Fi passwords, channel keys;
  - live `config.yaml` files.
- **Firmware release assets** carry checksums and source manifests. Verify them before flashing.
