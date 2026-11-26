---
default: patch
---

# Validate NOVEX updater public-key configuration

Reject malformed updater public-key values before release builds, including accidental pasting of the signer command instead of the minisign public key.
