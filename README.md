<div align="center">

<img src=".github/media/RepoBanner.png" alt="NOVEX Client repository banner" />

# NOVEX Client

NOVEX Client is an open-source Minecraft client and launcher based on the OneClient project by Polyfrost. It brings together a collection of packaged and pre-configured mods in one application.

</div>

## Installing

The current release target is **Windows (x86_64)**. Installers will be published on the [GitHub Releases page](https://github.com/divineiroinics/Novex_Client/releases) when a signed release has been configured and built.

macOS and Linux release installers are not currently part of the NOVEX release pipeline. The upstream project supports additional platforms, but those packages should not be treated as NOVEX-supported downloads yet.

### Automatic updates

The Windows updater verifies release signatures before installing an update. It remains disabled until the repository's persistent signing key pair is configured; this is a one-time maintainer setup described in [NOVEX release signing](docs/NOVEX-RELEASE-SIGNING.md).

The first key-enabled release must be downloaded and installed manually by existing users whose current build has no updater public key. Later signed releases can be detected and installed by the in-app updater. Windows Authenticode / SmartScreen publisher signing is separate and is not yet configured.

## Included NOVEX badge mod

The Windows release workflow reads the launcher's curated version catalog and builds and embeds a matching NOVEX badge mod for every listed **Fabric** game version. The build is discovered dynamically, so new Fabric versions in the catalog are picked up without editing a hardcoded version matrix. Forge, NeoForge, Quilt, and vanilla installations are not covered by this Fabric-only mod. Minecraft 26.x uses the new unobfuscated game namespace and requires a separate source port; the current Yarn-based implementation targets the legacy 1.x releases through 1.21.11.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) before getting started.

### Requirements

The project targets **Rust 1.97** or later. You can install Rust via [rustup](https://rustup.rs/).

### Building & Running

```sh
# Run the app
cargo run -p oneclient_app

# Build a release binary
cargo build -p oneclient_app --release
```

### Packaging / Releasing

Installers are produced with [**cargo-packager**](https://github.com/crabnebula-dev/cargo-packager). Configuration lives in [`packages/oneclient_app/Cargo.toml`](./packages/oneclient_app/Cargo.toml) under `[package.metadata.packager]`.

```sh
cargo install cargo-packager --version 0.11.8 --locked

# Build the binary, then bundle it for the current OS:
cargo build --release -p oneclient_app
cargo packager --release -p oneclient_app --formats nsis
```

The GitHub Actions release workflow currently packages Windows NSIS installers only. A release requires the updater signing secrets and public-key variable documented in [NOVEX release signing](docs/NOVEX-RELEASE-SIGNING.md).

### Versioning

The workspace shares a single version, defined in the root [`Cargo.toml`](./Cargo.toml) under `[workspace.package]`.

Versions and release notes come from Knope change files in [`.changeset/`](./.changeset). Add one per user-facing change with `knope document-change` (installed via `cargo install knope`). The release workflow consumes them, bumps the version, writes [`CHANGELOG.md`](./CHANGELOG.md), and uses the new entry as the GitHub release body.

## Original project and license

NOVEX Client is a fork of [OneLauncher / OneClient](https://github.com/Polyfrost/OneLauncher), originally developed by Polyfrost and contributors. The original project is licensed under the **GNU General Public License v3.0**. Original copyright notices, author credits, and license terms remain applicable to their respective code. NOVEX branding is maintained separately by XIRX.
