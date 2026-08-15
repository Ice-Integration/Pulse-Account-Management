#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn platform_name() -> String {
    std::env::consts::OS.to_string()
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![platform_name])
        .run(tauri::generate_context!())
        .expect("error while running Pulse desktop app");
}
