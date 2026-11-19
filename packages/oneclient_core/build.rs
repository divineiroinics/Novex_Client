use std::env;
use std::fs;
use std::path::PathBuf;

fn version_key(version: &str) -> (Vec<u32>, String) {
    let numeric = version.split('-').next().unwrap_or(version);
    let parts = numeric
        .split('.')
        .map(|part| part.parse().expect("badge jar version prefix must be numeric"))
        .collect();
    (parts, version.to_string())
}

fn is_supported_version_token(version: &str) -> bool {
    if !version
        .bytes()
        .all(|byte| byte.is_ascii_alphanumeric() || byte == b'.' || byte == b'-')
    {
        return false;
    }

    let mut segments = version.split('-');
    let numeric = segments.next().unwrap_or_default();
    !numeric.is_empty()
        && numeric.split('.').all(|part| {
            !part.is_empty() && part.bytes().all(|byte| byte.is_ascii_digit())
        })
        && segments.all(|part| {
            !part.is_empty() && part.bytes().all(|byte| byte.is_ascii_alphanumeric())
        })
}

fn main() {
    let manifest_dir = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest dir"));
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR"));
    println!("cargo:rerun-if-changed={}", manifest_dir.display());

    let mut jars = Vec::new();
    for entry in fs::read_dir(&manifest_dir).expect("read oneclient_core directory") {
        let entry = entry.expect("read staged badge jar entry");
        let path = entry.path();
        let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
            continue;
        };
        let Some(version) = name
            .strip_prefix("novex-badges-")
            .and_then(|name| name.strip_suffix(".jar"))
        else {
            continue;
        };
        if !is_supported_version_token(version) || !path.is_file() {
            continue;
        }

        println!("cargo:rerun-if-changed={}", path.display());
        let bytes = fs::metadata(&path)
            .unwrap_or_else(|err| panic!("failed to inspect {name}: {err}"))
            .len();
        if bytes == 0 {
            continue;
        }

        let out_jar = out_dir.join(name);
        fs::copy(&path, &out_jar)
            .unwrap_or_else(|err| panic!("failed to copy {name} into OUT_DIR: {err}"));
        jars.push((version.to_string(), name.to_string()));
    }

    jars.sort_by(|left, right| version_key(&left.0).cmp(&version_key(&right.0)));

    let mut generated = String::from("pub static MODS: &[(&str, &[u8])] = &[\n");
    for (version, name) in &jars {
        generated.push_str(&format!(
            "    ({version:?}, include_bytes!(concat!(env!(\"OUT_DIR\"), \"/{name}\"))),\n"
        ));
    }
    generated.push_str("];\n");

    fs::write(out_dir.join("novex_badge_mods.rs"), generated)
        .expect("write generated NOVEX badge mod registry");
}
