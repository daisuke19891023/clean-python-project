# 開発環境セットアップ手順

## 手動セットアップ

### pipxのインストール（入っていない場合）

```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

詳細は[pipxの公式ドキュメント](https://pipx.pypa.io/stable/installation/)を参照してください。

### uvのインストール

```bash
pipx install uv
```

詳細は[uvの公式ドキュメント](https://docs.astral.sh/uv/getting-started/installation/#configuring-installation)を参照してください。

### 対象のPythonバージョンのインストール

```bash
uv python install [TARGET_PYTHON_VERSION]
```

### 仮想環境の作成

```bash
uv venv
```

### ライブラリのインストール

```bash
uv sync
```

### pre-commitの設定

```bash
uv run pre-commit install
```

ここまでは`setup.sh`で実行できます

### noxの実行

```bash
uv run nox
```

### 仮想環境の有効化

```bash
source .venv/bin/activate
```

### 仮想環境の終了

```bash
deactivate
```

## 自動セットアップスクリプト

環境のセットアップを自動化するために、`setup.sh`スクリプトを用意しています。

### setup.shの使用方法

このスクリプトを使用することで、開発環境のセットアップを簡単に行うことができます。

1. `setup.sh`ファイルをプロジェクトのルートディレクトリに配置します。

2. スクリプトに実行権限を付与します：

   ```bash
   chmod +x setup.sh
   ```

3. スクリプトを実行します：

   ```bash
   ./setup.sh
   ```

注意事項：
- スクリプトはsudoコマンドを使用するため、実行時にパスワードの入力を求められる場合があります。
- Pythonのバージョンインストール行はデフォルトでコメントアウトされています。使用する場合は、スクリプトを編集し、適切なバージョン番号を指定してください。
- 仮想環境の有効化と終了は、スクリプト実行後に手動で行う必要があります。

