# NOVEX release signing

NOVEX updates are verified with cargo-packager signatures. Never commit the private signing key.

## One-time repository configuration

1. Generate a persistent key pair with the pinned cargo-packager tool using `cargo packager signer generate`.
2. Store the private key in the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY`.
3. Store its password in the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY_PASSWORD`.
4. Store the matching public key (the public half printed by the generator) in the repository Actions variable `NOVEX_UPDATER_PUBKEY`.

Keep this key pair stable for every release. Replacing it without a planned key rotation makes installed clients unable to verify future updates. The release workflow refuses to publish if the public key variable is missing. Nightly builds remain unsigned and keep automatic updates disabled. Windows code signing and Apple notarization use separate credentials.
