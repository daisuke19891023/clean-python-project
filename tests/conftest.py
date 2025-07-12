"""Pytest configuration for test_project tests."""

import json
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_json_data() -> dict[str, Any]:
    """Sample JSON data for testing."""
    return {
        "name": "Test Project",
        "version": "1.0.0",
        "description": "A test project for file operations",
        "features": ["logging", "file handling", "json support"],
        "config": {
            "debug": True,
            "max_connections": 100,
            "timeout": 30.5
        },
        "metadata": {
            "created": "2024-01-01T00:00:00Z",
            "updated": "2024-01-01T12:00:00Z"
        }
    }


@pytest.fixture
def sample_yaml_data() -> dict[str, Any]:
    """Sample YAML data for testing."""
    return {
        "application": {
            "name": "test-app",
            "version": "2.1.0",
            "environment": "production"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "testdb",
            "ssl": True
        },
        "services": [
            {"name": "api", "port": 8000},
            {"name": "worker", "port": 8001},
            {"name": "metrics", "port": 9090}
        ]
    }


@pytest.fixture
def sample_text_utf8() -> str:
    """Sample UTF-8 text with various characters."""
    return """Hello, World! 
こんにちは世界！
Здравствуй, мир!
¡Hola, mundo!
Emoji test: 🚀 🎉 📝
Special chars: ñáéíóú àèìòù äöü
Mathematical: α β γ δ ∑ ∫ π
"""


@pytest.fixture
def sample_text_cp932() -> str:
    """Sample CP932 (Shift-JIS) compatible text."""
    return """ファイルハンドラーのテスト
日本語の文字列をテストします。
これはCP932エンコーディング用のテストデータです。
"""


@pytest.fixture
def json_file_path(temp_dir: Path, sample_json_data: dict[str, Any]) -> Path:
    """Create a sample JSON file and return its path."""
    file_path = temp_dir / "sample.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(sample_json_data, f, indent=2, ensure_ascii=False)
    return file_path


@pytest.fixture
def yaml_file_path(temp_dir: Path, sample_yaml_data: dict[str, Any]) -> Path:
    """Create a sample YAML file and return its path."""
    file_path = temp_dir / "sample.yaml"
    with file_path.open("w", encoding="utf-8") as f:
        yaml.dump(sample_yaml_data, f, default_flow_style=False, allow_unicode=True)
    return file_path


@pytest.fixture
def utf8_file_path(temp_dir: Path, sample_text_utf8: str) -> Path:
    """Create a sample UTF-8 text file and return its path."""
    file_path = temp_dir / "sample_utf8.txt"
    file_path.write_text(sample_text_utf8, encoding="utf-8")
    return file_path


@pytest.fixture
def cp932_file_path(temp_dir: Path, sample_text_cp932: str) -> Path:
    """Create a sample CP932 text file and return its path."""
    file_path = temp_dir / "sample_cp932.txt"
    file_path.write_text(sample_text_cp932, encoding="cp932")
    return file_path


@pytest.fixture
def invalid_json_file_path(temp_dir: Path) -> Path:
    """Create an invalid JSON file for error testing."""
    file_path = temp_dir / "invalid.json"
    file_path.write_text('{"invalid": json, "missing": quote}', encoding="utf-8")
    return file_path


@pytest.fixture
def invalid_yaml_file_path(temp_dir: Path) -> Path:
    """Create an invalid YAML file for error testing."""
    file_path = temp_dir / "invalid.yaml"
    file_path.write_text("key:\n  - item1\n  - item2\n    - nested: but invalid indentation", encoding="utf-8")
    return file_path
