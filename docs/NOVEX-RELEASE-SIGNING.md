# NOVEX release signing

NOVEX updates are verified with cargo-packager signatures. Never commit the private signing key.

## One-time repository configuration

1. Generate a persistent key pair with the pinned cargo-packager tool using `cargo packager signer generate`.
2. Store the private key in the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY`.
3. Store its password in the repository Actions secret `CARGO_PACKAGER_SIGN_PRIVATE_KEY_PASSWORD`.
4. Store the matching public key (the public half printed by the generator) in the repository Actions variable `NOVEX_UPDATER_PUBKEY`.
5. Create a NOVEX project in SignPath and configure its Windows binary and installer artifact configurations with the repository's signing policy.
6. Store these SignPath values as repository Actions secrets:
   - `SIGNPATH_API_TOKEN`
   - `SIGNPATH_ORGANIZATION_ID`
7. Store these project-specific slugs as repository Actions variables:
   - `NOVEX_SIGNPATH_PROJECT_SLUG`
   - `NOVEX_SIGNPATH_BINARY_CONFIGURATION_SLUG`
   - `NOVEX_SIGNPATH_INSTALLER_CONFIGURATION_SLUG`

The release workflow now reads the SignPath project and artifact-configuration slugs from NOVEX variables. It no longer submits signing requests to the upstream OneLauncher SignPath project. A Windows release preflight checks that all required signing secrets and variables exist before building.

Keep the cargo-packager key pair stable for every release. Replacing it without a planned key rotation makes installed clients unable to verify future updates. Nightly builds remain unsigned and keep automatic updates disabled. Windows code signing and Apple notarization use separate credentials.
