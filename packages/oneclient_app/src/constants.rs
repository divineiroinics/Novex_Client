pub const WINDOW_APP_ID: &str = "org.xirx.NOVEXClient";
pub const WINDOW_TITLE: &str = "NOVEX Client";

pub const LATEST_RELEASE_URL: &str =
    "https://github.com/divineiroinics/Novex_Client/releases/latest/download/latest.json";
pub const RELEASES_URL: &str = "https://github.com/divineiroinics/Novex_Client/releases/latest";

// The public key is injected into release builds; unsigned nightly builds keep updates disabled.



pub const UPDATER_ENDPOINT: &str = "https://github.com/divineiroinics/Novex_Client/releases/latest/download/latest.json";

pub const UPDATER_PUBKEY: &str = match option_env!("NOVEX_UPDATER_PUBKEY") { Some(value) => value, None => "" };
