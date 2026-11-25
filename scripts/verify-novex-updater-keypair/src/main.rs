use base64::{engine::general_purpose::STANDARD, Engine as _};
use cargo_packager::sign::decode_private_key;
use minisign::PublicKey;
use std::{env, process};

fn main() {
    if let Err(error) = run() {
        eprintln!("::error::Could not validate NOVEX updater signing keys: {error}");
        process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let private_key = env::var("CARGO_PACKAGER_SIGN_PRIVATE_KEY")
        .map_err(|_| "CARGO_PACKAGER_SIGN_PRIVATE_KEY is missing")?;
    let password = env::var("CARGO_PACKAGER_SIGN_PRIVATE_KEY_PASSWORD").unwrap_or_default();
    let configured_public_key = env::var("NOVEX_UPDATER_PUBKEY").unwrap_or_default();

    // GitHub secret editors and copy/paste workflows can leave quote wrappers
    // in the value. Quotes are never valid in minisign's key-file encoding;
    // remove only those wrappers/noise before decoding. Never log this value.
    let normalized_private_key = private_key.replace('"', "");

    // Decode using the exact cargo-packager library used by the release workflow,
    // then derive the public key cryptographically. Never print or persist the secret.
    let secret_key = decode_private_key(&normalized_private_key, Some(&password))?;
    let public_key = PublicKey::from_secret_key(&secret_key)?;
    let public_key_box = public_key.to_box()?.to_string();
    let derived_public_key = STANDARD.encode(public_key_box);

    println!("Derived NOVEX_UPDATER_PUBKEY (safe to publish):");
    println!("{derived_public_key}");

    if configured_public_key.trim() != derived_public_key {
        return Err(concat!(
            "NOVEX_UPDATER_PUBKEY does not match CARGO_PACKAGER_SIGN_PRIVATE_KEY. ",
            "Set the repository Actions variable to the derived public key printed above, ",
            "then rerun this workflow. The private key was not printed."
        ).into());
    }

    println!("NOVEX updater public/private signing key pair matches.");
    Ok(())
}
