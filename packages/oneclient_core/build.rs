use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
    let manifest_dir = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest dir"));
    let staged_jar = manifest_dir.join("novex-badges-1.21.1.jar");
    let out_jar = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR"))
        .join("novex-badges-1.21.1.jar");

    println!("cargo:rerun-if-changed={}", staged_jar.display());

    if staged_jar.is_file() {
        fs::copy(&staged_jar, &out_jar)
            .expect("failed to copy staged NOVEX badge mod into OUT_DIR");
    } else {
        // Non-Windows and local builds can still compile without Java/Gradle.
        // The launcher simply skips auto-install when this placeholder is empty.
        fs::write(&out_jar, b"")
            .expect("failed to create empty NOVEX badge mod placeholder");
    }
}
