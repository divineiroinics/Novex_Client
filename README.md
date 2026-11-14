<div align="center">

<img src=".github/media/RepoBanner.png" alt="NOVEX Client repository banner" />

# NOVEX Client

NOVEX Client is an open-source Minecraft client and launcher based on the OneClient project by Polyfrost. It brings together a collection of packaged and pre-configured mods in one application.

</div>

## Installing

NOVEX Client releases will be published on the [GitHub Releases page](https://github.com/divineiroinics/Novex_Client/releases).

| Windows (x86_64) | macOS (Intel & Apple Silicon) | Linux (x86_64) |
|------------------|-------------------------------|----------------|
| Installer        | DMG                           | AppImage       |
|                  | App Bundle                    | DEB            |
|                  |                               | RPM            |

Release formats and built-in update support will be enabled as the NOVEX release pipeline is configured.

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

Installers are produced with [**cargo-packager**](https://github.com/crabnebula-dev/cargo-packager).
Configuration lives in [`packages/oneclient_app/Cargo.toml`](./packages/oneclient_app/Cargo.toml) under
`[package.metadata.packager]`.

```sh
cargo install cargo-packager --locked

# Build the binary, then bundle it for the current OS:
cargo build --release -p oneclient_app
cargo packager --release -p oneclient_app --formats <targets>
#   Windows: nsis      macOS: app,dmg      Linux: deb,appimage
```

### Versioning

The workspace shares a single version, defined in the root [`Cargo.toml`](./Cargo.toml) under
`[workspace.package]`.

Versions and release notes come from [Knope](https://knope.tech) change files in [`.changeset/`](./.changeset).
Add one per user-facing change with `knope document-change` (installed via `cargo install knope`).
The release workflow consumes them, bumps the version, writes [`CHANGELOG.md`](./CHANGELOG.md),
and uses the new entry as the GitHub release body.

## Original project and license

NOVEX Client is a fork of [OneLauncher / OneClient](https://github.com/Polyfrost/OneLauncher), originally developed by Polyfrost and contributors. The original project is licensed under the **GNU General Public License v3.0**. Original copyright notices, author credits, and license terms remain applicable to their respective code. NOVEX branding is maintained separately by XIRX.
