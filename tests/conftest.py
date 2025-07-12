"""Pytest configuration for test_project tests."""

import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_json_data() -> dict[str, Any]:
    """Sample JSON data for testing."""
    return {
        "name": "テストデータ",
        "id": 12345,
        "active": True,
        "items": [
            {"title": "アイテム1", "value": 100.5},
            {"title": "アイテム2", "value": 200.0},
        ],
        "metadata": {"created_at": "2024-01-01T00:00:00Z", "encoding": "utf-8"},
    }


@pytest.fixture
def sample_yaml_data() -> dict[str, Any]:
    """Sample YAML data for testing."""
    return {
        "name": "テストデータ",
        "id": 12345,
        "active": True,
        "items": [
            {"title": "アイテム1", "value": 100.5},
            {"title": "アイテム2", "value": 200.0},
        ],
        "metadata": {"created_at": "2024-01-01T00:00:00Z", "encoding": "utf-8"},
        "tags": ["development", "testing", "日本語"],
    }


@pytest.fixture
def sample_text_utf8() -> str:
    """Sample UTF-8 text for testing."""
    return """これはUTF-8でエンコードされたテストファイルです。
This is a test file encoded in UTF-8.

特殊文字のテスト:
- 漢字: 日本語テスト
- ひらがな: あいうえお
- カタカナ: アイウエオ
- 記号: ！？"#$%&'()

Multi-line content for testing:
Line 1: UTF-8 content
Line 2: 日本語コンテンツ
Line 3: Mixed content 混在コンテンツ"""


@pytest.fixture
def sample_text_cp932() -> str:
    """Sample CP932 text for testing."""
    return """これはCP932でエンコードされる予定のテストファイルです。
This is a test file to be encoded in CP932.

CP932特殊文字のテスト:
- 漢字: 日本語テスト  
- ひらがな: あいうえお
- カタカナ: アイウエオ
- 半角カナ: ｱｲｳｴｵ

CP932 encoding test content:
Line 1: Shift_JIS compatible content
Line 2: 日本語コンテンツ"""


@pytest.fixture
def temp_file_path() -> Path:
    """Temporary file path for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        return Path(tmp.name)


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_json_file(fixtures_dir: Path) -> Path:
    """Path to sample JSON file."""
    return fixtures_dir / "sample_data.json"


@pytest.fixture
def sample_yaml_file(fixtures_dir: Path) -> Path:
    """Path to sample YAML file."""
    return fixtures_dir / "sample_data.yaml"


@pytest.fixture
def sample_utf8_file(fixtures_dir: Path) -> Path:
    """Path to sample UTF-8 text file."""
    return fixtures_dir / "sample_text_utf8.txt"


@pytest.fixture
def sample_cp932_file(fixtures_dir: Path) -> Path:
    """Path to sample CP932 text file."""
    return fixtures_dir / "sample_text_cp932.txt"
