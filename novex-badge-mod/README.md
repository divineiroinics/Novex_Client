# NOVEX Badges (Fabric)

Client-side badge renderer for verified NOVEX Minecraft identities.

## Current build targets

The launcher build script discovers every stable Fabric entry in NOVEX's curated Minecraft version catalog and builds a separate matching jar. It also retains the previously shipped Minecraft 1.21.1, 1.21.4, 1.21.5, and 1.21.8 targets. Windows nightlies additionally attempt the newest Fabric preview in each source family (1.x and 26.x), plus the current modern weekly snapshot; previews are embedded only when mappings are available and compilation succeeds. Failed previews are skipped without failing the stable build, and signed releases remain stable-only. The current catalog includes these game-version families:

- Minecraft 1.18 through 1.21.11 (Yarn mappings; Java 17 or 21 according to the game version)
- Minecraft 26.x (Mojang's unobfuscated mappings; Java 25)

Minecraft versions before 1.18, older weekly snapshot identifiers, and non-Fabric loaders are not included; the latest current weekly snapshot is attempted in nightlies only. Forge, NeoForge, Quilt, and vanilla require separate loader-specific integrations. The catalog targets are discovered at build time rather than maintained as a hardcoded matrix; the four original targets are kept as backward-compatibility builds.

## Behavior

- Reads a player's UUID from the normal Minecraft client profile.
- Looks up verified identity and Standard/Plus tier through the NOVEX badge Edge Function.
- Caches results for 90 seconds and performs HTTP requests asynchronously.
- Adds a compact badge marker to player display names and player-list entries.
- Does not trust a username, client-supplied tier, or offline-mode UUID.

The database lookup only returns identities verified by Minecraft Services. When a player completes the launcher's existing Microsoft → Xbox → Minecraft sign-in, NOVEX sends the resulting short-lived Minecraft Services access token to its Edge Function. The function calls Minecraft's official profile endpoint, stores only the returned UUID and current username, and discards the token. The token is not written to logs or the database. Offline/cracked UUIDs cannot be verified this way and are not awarded globally trusted badges.

## Build

From the repository root, use Java 25, Gradle 9.8.0, and Python 3.9 or newer:

```sh
python scripts/build-novex-badge-mods.py
# Optional best-effort preview builds (used by Windows nightlies):
python scripts/build-novex-badge-mods.py --include-previews
```

The script reads NOVEX's version catalog, resolves the matching Yarn/Fabric Loader versions (or the modern Mojang-mapped toolchain), builds every supported variant, and stages the jars in `packages/oneclient_core/`. The launcher build then embeds the staged jars automatically.

## Launcher integration and privacy

The Windows nightly and release builds compile and embed every catalog-supported Fabric jar into NOVEX. On launch, the launcher installs the matching jar for the active Fabric Minecraft version without overwriting an existing file. The mod does not make badge requests unless the launcher has written a local consent marker after the user accepts the updated privacy notice. Declining the notice removes that marker.

The mod uses Fabric Loader and Minecraft classes only; it does not require Fabric API. Plus entitlement administration and end-to-end multiplayer/runtime testing still need completion. Do not advertise badges as fully verified until those tests pass.
