# FastHTTP GUI

FastHTTP has its own desktop GUI application — a visual interface for working with your requests, similar to Postman, but built specifically for FastHTTP.

## What is FastHTTP GUI?

FastHTTP GUI is a cross-platform desktop application built with [Tauri](https://tauri.app) that lets you:

- Build and send FastHTTP requests visually
- View request and response details in real time
- Manage request collections
- Work without writing code

## Installation

=== "Linux"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/ndugram/fasthttp/master/docs/install.sh | bash
    ```

    The script downloads the latest `.AppImage`, makes it executable and places it in `~/.local/bin/fasthttp-gui`.

    If `~/.local/bin` is not in your `PATH`, add this to your shell profile:

    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```

=== "macOS"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/ndugram/fasthttp/master/docs/install.sh | bash
    ```

    The script downloads the `.dmg`, mounts it and copies the `.app` to `/Applications`.

=== "Windows (PowerShell)"

    ```powershell
    irm https://raw.githubusercontent.com/ndugram/fasthttp/master/docs/install.ps1 | iex
    ```

    The script downloads and silently runs the `.msi` installer.

=== "Windows (Git Bash)"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/ndugram/fasthttp/master/docs/install.sh | bash
    ```

## Manual Download

You can also download the installer directly from the [GitHub Releases](https://github.com/ndugram/fasthttp-gui/releases/latest) page:

| Platform | File |
|---|---|
| Linux x86_64 | `fasthttp-gui_*_amd64.AppImage` |
| Linux x86_64 | `fasthttp-gui_*_amd64.deb` |
| Linux x86_64 | `fasthttp-gui-*-1.x86_64.rpm` |
| macOS Intel | `fasthttp-gui_*_x64.dmg` |
| macOS Apple Silicon | `fasthttp-gui_*_aarch64.dmg` |
| Windows x64 | `fasthttp-gui_*_x64_en-US.msi` |
| Windows x64 | `fasthttp-gui_*_x64-setup.exe` |

## Source Code

The source code is available on GitHub: [ndugram/fasthttp-gui](https://github.com/ndugram/fasthttp-gui)
