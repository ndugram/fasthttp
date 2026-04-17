# FastHTTP GUI

У FastHTTP есть собственное десктопное GUI-приложение — визуальный интерфейс для работы с запросами, похожий на Postman, но созданный специально для FastHTTP.

## Что такое FastHTTP GUI?

FastHTTP GUI — кроссплатформенное десктопное приложение на базе [Tauri](https://tauri.app), которое позволяет:

- Визуально составлять и отправлять FastHTTP-запросы
- Просматривать детали запросов и ответов в реальном времени
- Управлять коллекциями запросов
- Работать без написания кода

## Установка

=== "Linux"

    ```bash
    curl -fsSL https://fasthttp.ndugram.dev/install.sh | bash
    ```

    Скрипт скачивает последний `.AppImage`, делает его исполняемым и кладёт в `~/.local/bin/fasthttp-gui`.

    Если `~/.local/bin` не в вашем `PATH`, добавьте в профиль оболочки:

    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```

=== "macOS"

    ```bash
    curl -fsSL https://fasthttp.ndugram.dev/install.sh | bash
    ```

    Скрипт скачивает `.dmg`, монтирует его и копирует `.app` в `/Applications`.

=== "Windows (PowerShell)"

    ```powershell
    irm https://fasthttp.ndugram.dev/install.ps1 | iex
    ```

    Скрипт скачивает и запускает `.msi` установщик в тихом режиме.

=== "Windows (Git Bash)"

    ```bash
    curl -fsSL https://fasthttp.ndugram.dev/install.sh | bash
    ```

## Скачать вручную

Также можно скачать установщик напрямую со страницы [GitHub Releases](https://github.com/ndugram/fasthttp-gui/releases/latest):

| Платформа | Файл |
|---|---|
| Linux x86_64 | `fasthttp-gui_*_amd64.AppImage` |
| Linux x86_64 | `fasthttp-gui_*_amd64.deb` |
| Linux x86_64 | `fasthttp-gui-*-1.x86_64.rpm` |
| macOS Intel | `fasthttp-gui_*_x64.dmg` |
| macOS Apple Silicon | `fasthttp-gui_*_aarch64.dmg` |
| Windows x64 | `fasthttp-gui_*_x64_en-US.msi` |
| Windows x64 | `fasthttp-gui_*_x64-setup.exe` |

## Исходный код

Исходный код доступен на GitHub: [ndugram/fasthttp-gui](https://github.com/ndugram/fasthttp-gui)
