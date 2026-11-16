fn main() {
    #[cfg(windows)]
    {
        let mut res = winresource::WindowsResource::new();
        res.set_icon("icons/icon.ico");

        let version = env!("CARGO_PKG_VERSION");
        res.set("CompanyName", "XIRX");
        res.set("ProductName", "NOVEX Client");
        res.set("FileDescription", "NOVEX Client");
        res.set("LegalCopyright", "© 2026 XIRX. Original code © 2026 Polyfrost Inc. and contributors.");
        res.set("OriginalFilename", "oneclient_app.exe");
        res.set("InternalName", "oneclient_app");
        res.set("FileVersion", version);
        res.set("ProductVersion", version);

        res.compile()
            .expect("failed to embed Windows icon resource");
    }
}
