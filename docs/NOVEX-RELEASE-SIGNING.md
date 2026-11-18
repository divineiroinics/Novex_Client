# NOVEX automatic update signing

NOVEX automatic updates use cargo-packager signatures. The public key is embedded in release builds; the matching private key is used only by GitHub Actions to sign each Windows installer. Never commit or share the private key.

## One-time repository configuration

1. On a trusted local machine, use the same pinned cargo-packager version as the release workflow (`0.11.8`) and run `cargo packager signer generate`.
2. Save the generated private key and its password securely. Do not paste either into chat, an issue, a commit, or a workflow file.
3. Add the private key as the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY`.
4. If the private key is password-protected, add its password as the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY_PASSWORD`. If you generated an unencrypted key, leave this secret unset; the release workflow passes an empty password to cargo-packager, which explicitly skips its interactive password prompt.
5. Add the matching public key as the repository Actions variable `NOVEX_UPDATER_PUBKEY`.

The Windows release workflow requires the public key and private key before building. The password secret is optional for unencrypted keys. It signs the Windows installer with the cargo-packager key, writes the matching signature into the update manifest, validates the manifest, uploads `latest.json`, and only then publishes the GitHub release. This order ensures the public `/releases/latest/download/latest.json` endpoint cannot point at a draft or incomplete release.

## Key safety

- Keep this key pair stable across releases. Replacing it without a planned key rotation prevents already-installed clients from verifying future updates.
- The private key and password must remain GitHub Actions secrets. The public key is safe to store as a repository Actions variable.
- Nightly builds remain unsigned and do not auto-update.
- Windows Authenticode / SmartScreen signing is separate and intentionally not required for the updater signature. It can be added later without changing the updater trust key.
