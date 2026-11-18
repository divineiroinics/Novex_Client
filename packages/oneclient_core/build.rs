use std::env;
use std::fs;
use std::path::PathBuf;

const SUPPORTED: &[&str] = &["1.21.1", "1.21.4", "1.21.5", "1.21.8"];

fn main() {
    let manifest_dir = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest dir"));
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR"));

    for version in SUPPORTED {
        let name = format!("novex-badges-{version}.jar");
        let staged_jar = manifest_dir.join(&name);
        let out_jar = out_dir.join(&name);
        println!("cargo:rerun-if-changed={}", staged_jar.display());

        if staged_jar.is_file() {
            fs::copy(&staged_jar, &out_jar)
                .unwrap_or_else(|err| panic!("failed to copy {name} into OUT_DIR: {err}"));
        } else {
            // Local and non-Windows builds remain buildable without Java/Gradle.
            // Auto-install is skipped for versions whose jar is not embedded.
            fs::write(&out_jar, b"")
                .unwrap_or_else(|err| panic!("failed to create empty {name} placeholder: {err}"));
        }
    }
}
