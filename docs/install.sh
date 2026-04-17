#!/usr/bin/env bash
set -euo pipefail

REPO="ndugram/fasthttp-gui"
BIN_NAME="fasthttp-gui"

detect_os() {
  case "$(uname -s)" in
    Linux*)               echo "linux" ;;
    Darwin*)              echo "macos" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *)
      echo "Unsupported OS: $(uname -s)" >&2
      exit 1
      ;;
  esac
}

detect_arch() {
  case "$(uname -m)" in
    x86_64)        echo "x86_64" ;;
    arm64|aarch64) echo "aarch64" ;;
    *)
      echo "Unsupported architecture: $(uname -m)" >&2
      exit 1
      ;;
  esac
}

fetch_release_data() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest"
}

get_asset_url() {
  local data="$1" pattern="$2"
  echo "$data" \
    | grep '"browser_download_url"' \
    | grep -i "$pattern" \
    | head -1 \
    | sed -E 's/.*"([^"]+)".*/\1/'
}

install_linux() {
  local data="$1" arch="$2"
  local url=""

  if [ "$arch" = "x86_64" ]; then
    url=$(get_asset_url "$data" "amd64\.AppImage")
    [ -z "$url" ] && url=$(get_asset_url "$data" "x86_64.*\.AppImage")
  else
    url=$(get_asset_url "$data" "aarch64.*\.AppImage")
  fi

  if [ -z "$url" ]; then
    echo "No AppImage found for ${arch}" >&2
    exit 1
  fi

  local install_dir="${HOME}/.local/bin"
  mkdir -p "$install_dir"

  local tmp
  tmp=$(mktemp)
  trap "rm -f $tmp" RETURN

  echo "Downloading: $url"
  curl -fsSL "$url" -o "$tmp"
  install -m 755 "$tmp" "${install_dir}/${BIN_NAME}"
  echo "Installed to ${install_dir}/${BIN_NAME}"

  if ! echo "${PATH}" | grep -q "${install_dir}"; then
    echo ""
    echo "Add to your shell profile:"
    echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
  fi
}

install_macos() {
  local data="$1" arch="$2"
  local url=""

  if [ "$arch" = "aarch64" ]; then
    url=$(get_asset_url "$data" "aarch64.*\.dmg")
  else
    url=$(get_asset_url "$data" "x64\.dmg")
    [ -z "$url" ] && url=$(get_asset_url "$data" "x86_64.*\.dmg")
  fi

  if [ -z "$url" ]; then
    echo "No DMG found for ${arch}" >&2
    exit 1
  fi

  local tmp_dir
  tmp_dir=$(mktemp -d)
  trap "rm -rf $tmp_dir" RETURN

  local dmg="${tmp_dir}/${BIN_NAME}.dmg"
  local mount_point="${tmp_dir}/mount"

  echo "Downloading: $url"
  curl -fsSL "$url" -o "$dmg"

  mkdir -p "$mount_point"
  hdiutil attach "$dmg" -mountpoint "$mount_point" -quiet -nobrowse

  local app
  app=$(find "$mount_point" -maxdepth 1 -name "*.app" | head -1)

  if [ -z "$app" ]; then
    hdiutil detach "$mount_point" -quiet
    echo "No .app found inside DMG" >&2
    exit 1
  fi

  local app_name
  app_name=$(basename "$app")
  rm -rf "/Applications/${app_name}"
  cp -r "$app" /Applications/
  hdiutil detach "$mount_point" -quiet

  echo "Installed to /Applications/${app_name}"
}

install_windows_gitbash() {
  local data="$1"
  local url=""

  url=$(get_asset_url "$data" "x64.*\.msi")
  [ -z "$url" ] && url=$(get_asset_url "$data" "x64.*setup.*\.exe")
  [ -z "$url" ] && url=$(get_asset_url "$data" "\.msi")

  if [ -z "$url" ]; then
    echo "No Windows installer found" >&2
    exit 1
  fi

  local filename
  filename=$(basename "$url")
  local tmp="${TEMP:-/tmp}/${filename}"

  echo "Downloading: $url"
  curl -fsSL "$url" -o "$tmp"

  echo "Running installer..."
  if [[ "$filename" == *.msi ]]; then
    msiexec.exe /i "$(cygpath -w "$tmp")" /passive
  else
    "$(cygpath -w "$tmp")" /passive
  fi

  rm -f "$tmp"
  echo "Installation complete"
}

main() {
  local OS ARCH data VERSION
  OS=$(detect_os)
  ARCH=$(detect_arch)

  data=$(fetch_release_data)
  VERSION=$(echo "$data" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

  if [ -z "$VERSION" ]; then
    echo "Failed to fetch latest release version" >&2
    exit 1
  fi

  echo "Installing ${BIN_NAME} ${VERSION} for ${OS}/${ARCH}..."

  case "$OS" in
    linux)   install_linux "$data" "$ARCH" ;;
    macos)   install_macos "$data" "$ARCH" ;;
    windows) install_windows_gitbash "$data" ;;
  esac
}

main "$@"
