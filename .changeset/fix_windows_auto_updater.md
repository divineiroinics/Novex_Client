---
default: patch
---

# Fix Windows automatic update publishing

Publish the Windows update manifest only after its installer and signature are ready, validate the manifest, and then publish the release.