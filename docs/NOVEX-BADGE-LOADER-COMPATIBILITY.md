# NOVEX badge loader compatibility

This document describes the badge integration as it exists today. A loader being supported by the launcher does **not** automatically mean the NOVEX badge mod can run on it.

| Minecraft profile | Badge status | Reason |
| --- | --- | --- |
| Fabric | Supported by the bundled badge integration for versions present in the generated catalog | The badge mod is built with Fabric Loom and installed into the profile's mods directory. |
| Quilt | Compatibility path; requires runtime verification | Quilt's Fabric compatibility layer is used to load the Fabric badge jar. |
| Forge | Not implemented | The current badge jar declares Fabric entrypoints and Fabric mixins; it is not a Forge mod. |
| NeoForge | Not implemented | No NeoForge-native badge artifact or verified compatibility-layer path is currently shipped. |
| Vanilla | Not implemented | Vanilla does not load ordinary Fabric/Forge/NeoForge mod jars. A separate injection or client-side integration would be required. |
| Ornithe | Not implemented | No Ornithe-native badge artifact or verified compatibility path is currently shipped. |

## Safety and user data

- NOVEX does not copy a Fabric jar into Forge, NeoForge, vanilla, or Ornithe profiles.
- The launcher preserves a user-managed jar if the destination filename already exists but does not match the hash of the previously managed NOVEX jar.
- Badge lookups remain gated by the user's badge privacy consent.
- A successful build of the Fabric jar is not proof that it renders correctly in a live Minecraft session.

## Work required for additional loaders

1. Forge: create and test a Forge-native badge module for each supported Minecraft/Forge API family.
2. NeoForge: create and test a NeoForge-native badge module; do not assume Forge compatibility.
3. Vanilla: design a separate supported client integration/injection mechanism, or explicitly keep vanilla badge rendering unsupported.
4. Quilt: test the bundled Fabric compatibility route in actual Quilt game instances across representative Minecraft versions.
5. Add per-loader build, packaging, and launch tests before marking any loader supported.
