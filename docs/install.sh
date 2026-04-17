#!/usr/bin/env bash
set -euo pipefail

REPO="ndugram/fasthttp-gui"
BIN_NAME="fasthttp-gui"
INSTALL_DIR="${HOME}/.local/bin"

detect_os() {
  case "$(uname -s)" in
    Linux*)  echo "linux" ;;
    Darwin*) echo "macos" ;;
    *)
      echo "Unsupported OS: $(uname -s)" >&2
      exit 1
      ;;
  esac
}

detect_arch() {
  case "$(uname -m)" in
    x86_64)  echo "x86_64" ;;
    arm64|aarch64) echo "aarch64" ;;
    *)
      echo "Unsupported architecture: $(uname -m)" >&2
      exit 1
      ;;
  esac
}

fetch_latest_version() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | grep '"tag_name"' \
    | sed -E 's/.*"([^"]+)".*/\1/'
}

main() {
  OS=$(detect_os)
  ARCH=$(detect_arch)
  VERSION=$(fetch_latest_version)

  if [ -z "$VERSION" ]; then
    echo "Failed to fetch latest release version." >&2
    exit 1
  fi

  echo "Installing ${BIN_NAME} ${VERSION} for ${OS}/${ARCH}..."

  case "${OS}" in
    linux)
      ASSET="${BIN_NAME}_${VERSION#v}_${ARCH}-unknown-linux-gnu.tar.gz"
      ;;
    macos)
      ASSET="${BIN_NAME}_${VERSION#v}_${ARCH}-apple-darwin.tar.gz"
      ;;
  esac

  TMP_DIR=$(mktemp -d)
  trap 'rm -rf "${TMP_DIR}"' EXIT

  DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${VERSION}/${ASSET}"
  echo "Downloading from: ${DOWNLOAD_URL}"

  curl -fsSL "${DOWNLOAD_URL}" -o "${TMP_DIR}/${ASSET}"
  tar -xzf "${TMP_DIR}/${ASSET}" -C "${TMP_DIR}"

  mkdir -p "${INSTALL_DIR}"
  install -m 755 "${TMP_DIR}/${BIN_NAME}" "${INSTALL_DIR}/${BIN_NAME}"

  echo "Installed to ${INSTALL_DIR}/${BIN_NAME}"

  if ! echo "${PATH}" | grep -q "${INSTALL_DIR}"; then
    echo ""
    echo "Add the following to your shell profile to use ${BIN_NAME}:"
    echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
  fi
}

main "$@"
