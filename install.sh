#!/usr/bin/env bash
set -euo pipefail

REPO_URL="git+https://github.com/mohammadameer/quran-tui.git"

log() {
  printf "%s\n" "$1"
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

install_with_apt() {
  sudo apt-get update
  sudo apt-get install -y python3 python3-pip pipx git curl
}

install_with_dnf() {
  sudo dnf install -y python3 python3-pip pipx git curl
}

install_with_pacman() {
  sudo pacman -Sy --noconfirm python python-pip python-pipx git curl
}

install_with_zypper() {
  sudo zypper --non-interactive install python3 python3-pip pipx git curl
}

install_with_apk() {
  sudo apk add --no-cache python3 py3-pip pipx git curl
}

install_linux_deps() {
  if has_cmd apt-get; then
    install_with_apt
    return
  fi
  if has_cmd dnf; then
    install_with_dnf
    return
  fi
  if has_cmd pacman; then
    install_with_pacman
    return
  fi
  if has_cmd zypper; then
    install_with_zypper
    return
  fi
  if has_cmd apk; then
    install_with_apk
    return
  fi
  log "Unsupported Linux package manager. Install python3, pipx, git, curl manually."
  exit 1
}

install_macos_deps() {
  if ! has_cmd brew; then
    log "Homebrew not found. Install Homebrew first: https://brew.sh"
    exit 1
  fi
  brew install python pipx git curl
}

ensure_pipx() {
  if has_cmd pipx; then
    return
  fi

  if has_cmd python3; then
    python3 -m pip install --user --upgrade pip pipx
    export PATH="$HOME/.local/bin:$PATH"
    return
  fi

  log "python3 not found."
  exit 1
}

main() {
  os_name="$(uname -s)"
  case "$os_name" in
    Linux*)
      log "Detected Linux. Installing deps..."
      install_linux_deps
      ;;
    Darwin*)
      log "Detected macOS. Installing deps..."
      install_macos_deps
      ;;
    *)
      log "Unsupported OS: $os_name"
      exit 1
      ;;
  esac

  ensure_pipx
  pipx ensurepath >/dev/null || true
  pipx install --force "$REPO_URL"
  export PATH="$HOME/.local/bin:$PATH"
  log "Downloading Quran data..."
  quran --download-data || true
  log "Installed. Run: quran"
}

main "$@"
