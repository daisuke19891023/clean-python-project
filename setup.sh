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

# --- License Text Functions ---
source ./license_utils.sh

# --- Interactive Prompts ---
info "プロジェクト情報を入力してください:"
read -p "プロジェクト名: " PROJECT_NAME
read -p "プロジェクトの説明: " PROJECT_DESCRIPTION

# Input validation for LIBRARY_NAME
while true; do
    read -p "src/ ディレクトリのベースライブラリ名 (例: my_library): " LIBRARY_NAME
    if [[ -z "$LIBRARY_NAME" ]]; then
        echo "エラー: ライブラリ名は空にできません。"
    elif ! [[ "$LIBRARY_NAME" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
        echo "エラー: ライブラリ名が無効です。英数字とアンダースコアのみを使用し、先頭は英字またはアンダースコアにしてください。"
    else
        break
    fi
done

info "ライセンスタイプを選択してください:"
select LICENSE_TYPE_CHOICE in "MIT" "Apache-2.0" "GPL-3.0"; do
    if [[ -n "$LICENSE_TYPE_CHOICE" ]]; then
        LICENSE_TYPE=$LICENSE_TYPE_CHOICE
        break
    else
        echo "無効な選択です。もう一度選択してください。"
    fi
done
read -p "著作権者: " COPYRIGHT_HOLDER

# --- Generate PROJECT_NAME_SLUG ---
info "PROJECT_NAME_SLUGを生成しています..."
PROJECT_NAME_SLUG=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9-]/-/g' -e 's/-\{2,\}/-/g' -e 's/^-//' -e 's/-$//')
success "PROJECT_NAME_SLUGが生成されました: $PROJECT_NAME_SLUG"

# --- Create Library Directory ---
info "ライブラリディレクトリを作成しています..."
mkdir -p "src/$LIBRARY_NAME"
touch "src/$LIBRARY_NAME/__init__.py"
success "ライブラリディレクトリ src/$LIBRARY_NAME が作成されました"

# --- Perform File Content Updates ---
CURRENT_YEAR=$(date +%Y)

info "README.mdを更新しています..."
sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" README.md
sed -i "s/{{PROJECT_DESCRIPTION}}/$PROJECT_DESCRIPTION/g" README.md
sed -i "s/{{LICENSE_TYPE}}/$LICENSE_TYPE/g" README.md
sed -i "s/{{PROJECT_NAME_SLUG}}/$PROJECT_NAME_SLUG/g" README.md
success "README.mdが更新されました"

info "pyproject.tomlを更新しています..."
sed -i "s/name = \"{{PROJECT_NAME}}\"/name = \"$PROJECT_NAME_SLUG\"/g" pyproject.toml
sed -i "s/description = \"{{PROJECT_DESCRIPTION}}\"/description = \"$PROJECT_DESCRIPTION\"/g" pyproject.toml
sed -i "s|--cov=src|--cov=src/$LIBRARY_NAME|g" pyproject.toml
sed -i "s|include = \[\"src\"\]|include = \[\"src/$LIBRARY_NAME\"\]|g" pyproject.toml
success "pyproject.tomlが更新されました"

info "mkdocs.ymlを更新しています..."
sed -i "s/site_name: {{PROJECT_NAME}}/site_name: $PROJECT_NAME/g" mkdocs.yml
sed -i "s/site_description: {{PROJECT_DESCRIPTION}}/site_description: $PROJECT_DESCRIPTION/g" mkdocs.yml
success "mkdocs.ymlが更新されました"

info "LICENSEファイルを更新しています..."
if [ "$LICENSE_TYPE" == "MIT" ]; then
    get_mit_license_text > LICENSE
elif [ "$LICENSE_TYPE" == "Apache-2.0" ]; then
    get_apache_license_text > LICENSE
elif [ "$LICENSE_TYPE" == "GPL-3.0" ]; then
    get_gplv3_license_text > LICENSE
fi
success "LICENSEファイルが更新されました"


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
# Unset core.hooksPath and temporarily isolate from global/system git config
(export GIT_CONFIG_GLOBAL=/dev/null; export GIT_CONFIG_SYSTEM=/dev/null; git config --unset-all core.hooksPath || true; uv run pre-commit install) || error "pre-commitの設定に失敗しました"
success "pre-commitが設定されました"

info "ローカル環境のセットアップが完了しました"
info "DevContainerを使用する場合は、VS Codeで「Reopen in Container」を選択してください"
