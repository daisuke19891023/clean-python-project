#!/bin/bash

set -e

# Function to print error messages
error() {
    echo "エラー: $1" >&2
    exit 1
}

# Function to print success messages
success() {
    echo "成功: $1"
}

# Function to print info messages
info() {
    echo "情報: $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install pipx if not already installed
if ! command_exists pipx; then
    info "pipxをインストールしています..."
    sudo apt update || error "apt updateに失敗しました"
    sudo apt install -y pipx || error "pipxのインストールに失敗しました"
    pipx ensurepath || error "pipx ensurepath に失敗しました"
    success "pipxがインストールされました"
else
    info "pipxは既にインストールされています"
fi

# Install uv if not already installed
if ! command_exists uv; then
    info "uvをインストールしています..."
    pipx install uv || error "uvのインストールに失敗しました"
    success "uvがインストールされました"
else
    info "uvは既にインストールされています"
fi

# Install target Python version (uncomment and replace X.X with desired version)
# TARGET_PYTHON_VERSION="X.X"
# if ! command_exists "python$TARGET_PYTHON_VERSION"; then
#     info "Python $TARGET_PYTHON_VERSION をインストールしています..."
#     uv python install $TARGET_PYTHON_VERSION || error "Python $TARGET_PYTHON_VERSION のインストールに失敗しました"
#     success "Python $TARGET_PYTHON_VERSION がインストールされました"
# else
#     info "Python $TARGET_PYTHON_VERSION は既にインストールされています"
# fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    info "仮想環境を作成しています..."
    uv venv || error "仮想環境の作成に失敗しました"
    success "仮想環境が作成されました"
else
    info "仮想環境は既に存在します"
fi

# Install dependencies
info "依存関係をインストールしています..."
uv sync || error "依存関係のインストールに失敗しました"
success "依存関係がインストールされました"

# Set up pre-commit
info "pre-commitを設定しています..."
uv run pre-commit install || error "pre-commitの設定に失敗しました"
success "pre-commitが設定されました"

info "セットアップが完了しました"