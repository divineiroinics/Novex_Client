<div align="center">

<img src=".github/media/RepoBanner.png" alt="NOVEX Client repository banner" />

# NOVEX Client

NOVEX Client is an open-source Minecraft client and launcher maintained and branded by XIRX. It preserves the original launcher experience while bringing together a collection of packaged and pre-configured mods in one application.

</div>

## Installing

The current release target is **Windows (x86_64)**. The latest signed Windows release is [NOVEX Client 2.11.5](https://github.com/divineiroinics/Novex_Client/releases/tag/novex-2.11.5). Download the [Windows x86_64 installer](https://github.com/divineiroinics/Novex_Client/releases/download/novex-2.11.5/NOVEX_Client_2.11.5_windows_x86_64.exe) or browse the [GitHub Releases page](https://github.com/divineiroinics/Novex_Client/releases).

macOS and Linux release installers are not currently part of the NOVEX release pipeline. The upstream project supports additional platforms, but those packages should not be treated as NOVEX-supported downloads yet.

### Automatic updates

The Windows updater verifies release signatures before installing an update. The persistent NOVEX updater key pair is configured in GitHub Actions and the public key is embedded in signed release builds. The release workflow signs each installer, publishes its signature in `latest.json`, and validates the manifest before making the release latest. See [NOVEX release signing](docs/NOVEX-RELEASE-SIGNING.md) for key management.

Users upgrading from an older build that does not contain the NOVEX updater public key must install 2.11.5 manually once. A Windows CI smoke test has since installed 2.11.5, downloaded the signed 2.11.6 update, verified its signature, ran the installer, and confirmed that the installed executable changed. Automatic installation during normal launcher startup is a separate change scheduled for 2.11.7; Windows Authenticode / SmartScreen publisher signing is also separate and is not yet configured.

## Included NOVEX badge mod

The Windows release workflow reads the launcher's curated version catalog and dynamically builds and embeds a matching NOVEX badge mod for every listed **stable Fabric** target (currently Minecraft 1.18–1.21.11 and 26+), while retaining the previously shipped 1.21.1, 1.21.4, 1.21.5, and 1.21.8 builds. Windows nightlies also best-effort build the newest Fabric snapshot/RC/pre-release in the legacy 1.x and modern 26+ families, plus the newest modern weekly snapshot. A preview is embedded only when matching Fabric mappings and a loader are available and the current badge source compiles; incompatible previews are skipped without blocking stable builds. Preview support is experimental and is not included in signed releases. Forge, NeoForge, Quilt, and vanilla installations are not covered by this Fabric-only mod. Versions before 1.18 and older weekly snapshot identifiers are not included.

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
