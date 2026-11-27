use std::{env, error::Error};

use cargo_packager_updater::{check_update, Config, WindowsConfig};
use semver::Version;

const ENDPOINT: &str =
    "https://github.com/divineiroinics/Novex_Client/releases/latest/download/latest.json";

fn main() -> Result<(), Box<dyn Error>> {
    let current_version = env::args()
        .nth(1)
        .ok_or("pass the installed NOVEX version as the first argument")?;
    let current_version = Version::parse(&current_version)?;
    let public_key = env::var("NOVEX_UPDATER_PUBKEY")?;

    let config = Config {
        endpoints: vec![ENDPOINT.parse()?],
        pubkey: public_key,
        windows: Some(WindowsConfig {
            installer_args: Some(vec!["/NS".into()]),
            ..Default::default()
        }),
    };

    let update = check_update(current_version, config)?
        .ok_or("the signed NOVEX release feed did not offer an update")?;
    println!("Found signed NOVEX update {}.", update.version);

    // download() verifies the downloaded installer against the manifest signature
    // and the same public key embedded in the production launcher.
    let installer = update.download()?;
    println!("Installer download and signature verification passed.");

    // On Windows, the NSIS updater starts the installer and exits this process.
    update.install(installer)?;
    Ok(())
}
