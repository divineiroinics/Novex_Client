use base64::{engine::general_purpose::STANDARD, Engine as _};
use cargo_packager::sign::decode_private_key;
use minisign::PublicKey;
use std::{env, io, process};

fn normalize_private_key(value: &str) -> String {
    value
        .chars()
        .filter(|character| character.is_ascii_alphanumeric() || matches!(*character, '+' | '/' | '='))
        .collect()
}

fn pad_base64(value: &str) -> Result<String, &'static str> {
    match value.len() % 4 {
        0 => Ok(value.to_owned()),
        2 => Ok(format!("{value}==")),
        3 => Ok(format!("{value}=")),
        _ => Err("normalized key has an impossible Base64 length (length modulo 4 is 1); the secret is truncated or contains missing characters"),
    }
}

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

    // Remove accidental copy/paste punctuation and whitespace, but never log
    // the secret or any portion of it.
    let normalized_private_key = normalize_private_key(&private_key);
    let padded_private_key = pad_base64(&normalized_private_key).map_err(|error| {
        io::Error::new(
            io::ErrorKind::InvalidData,
            format!(
                "{error}; observed normalized character count: {}",
                normalized_private_key.len()
            ),
        )
    })?;

    // A missing Base64 '=' suffix is recoverable. Missing data is not; report
    // only the encoded length if cargo-packager still rejects the value.
    let secret_key = decode_private_key(&padded_private_key, Some(&password)).map_err(|error| {
        io::Error::new(
            io::ErrorKind::InvalidData,
            format!(
                "cargo-packager rejected the normalized key (encoded character count: {}, modulo 4: {}): {error}",
                padded_private_key.len(),
                padded_private_key.len() % 4
            ),
        )
    })?;
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_copy_paste_noise_around_base64() {
        let normalized = normalize_private_key("  \"YWJj$\\nZGVm!\"  ");
        assert_eq!(normalized, "YWJjZGVm");
    }

    #[test]
    fn restores_missing_base64_padding() {
        assert_eq!(pad_base64("YWJjZA").unwrap(), "YWJjZA==");
        assert_eq!(pad_base64("YWJjZ").unwrap(), "YWJjZ=");
        assert_eq!(pad_base64("YWJj").unwrap(), "YWJj");
    }

    #[test]
    fn rejects_truncated_base64_length() {
        assert!(pad_base64("Y").is_err());
    }
}
