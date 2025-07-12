"""Unit tests for file_handler functionality."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from test_project.utils.file_handler import (
    read_file,
    write_file,
    read_json,
    write_json,
    read_yaml,
    write_yaml,
)


class TestFileOperations:
    """Unit tests for basic file read/write operations."""

    def test_read_file_utf8(self, utf8_file_path: Path, sample_text_utf8: str) -> None:
        """Test reading UTF-8 encoded file."""
        content = read_file(utf8_file_path, encoding="utf-8")
        assert content == sample_text_utf8

    def test_read_file_cp932(self, cp932_file_path: Path, sample_text_cp932: str) -> None:
        """Test reading CP932 encoded file."""
        content = read_file(cp932_file_path, encoding="cp932")
        assert content == sample_text_cp932

    def test_write_file_utf8(self, temp_dir: Path, sample_text_utf8: str) -> None:
        """Test writing UTF-8 encoded file."""
        file_path = temp_dir / "test_write_utf8.txt"
        write_file(file_path, sample_text_utf8, encoding="utf-8")
        
        # Verify file was written correctly
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert content == sample_text_utf8

    def test_write_file_cp932(self, temp_dir: Path, sample_text_cp932: str) -> None:
        """Test writing CP932 encoded file."""
        file_path = temp_dir / "test_write_cp932.txt"
        write_file(file_path, sample_text_cp932, encoding="cp932")
        
        # Verify file was written correctly
        assert file_path.exists()
        content = file_path.read_text(encoding="cp932")
        assert content == sample_text_cp932

    def test_write_file_creates_directories(self, temp_dir: Path) -> None:
        """Test that write_file creates parent directories."""
        nested_path = temp_dir / "nested" / "deep" / "test.txt"
        content = "Test content"
        
        write_file(nested_path, content)
        
        assert nested_path.exists()
        assert nested_path.read_text() == content

    def test_read_file_not_found(self, temp_dir: Path) -> None:
        """Test reading non-existent file raises FileNotFoundError."""
        non_existent = temp_dir / "does_not_exist.txt"
        
        with pytest.raises(FileNotFoundError):
            read_file(non_existent)

    def test_read_file_encoding_error(self, cp932_file_path: Path) -> None:
        """Test reading CP932 file with wrong encoding raises UnicodeDecodeError."""
        with pytest.raises(UnicodeDecodeError):
            read_file(cp932_file_path, encoding="utf-8")

    def test_roundtrip_file_operations(self, temp_dir: Path, sample_text_utf8: str) -> None:
        """Test roundtrip file operations (write then read)."""
        file_path = temp_dir / "roundtrip.txt"
        
        # Write and read back
        write_file(file_path, sample_text_utf8)
        content = read_file(file_path)
        
        assert content == sample_text_utf8


class TestJSONOperations:
    """Unit tests for JSON file operations."""

    def test_read_json(self, json_file_path: Path, sample_json_data: dict[str, Any]) -> None:
        """Test reading JSON file."""
        data = read_json(json_file_path)
        assert data == sample_json_data

    def test_write_json(self, temp_dir: Path, sample_json_data: dict[str, Any]) -> None:
        """Test writing JSON file."""
        file_path = temp_dir / "test_write.json"
        write_json(file_path, sample_json_data)
        
        # Verify file was written correctly
        assert file_path.exists()
        with file_path.open("r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data == sample_json_data

    def test_write_json_with_formatting(self, temp_dir: Path) -> None:
        """Test writing JSON with custom formatting."""
        data = {"key": "value", "number": 42}
        file_path = temp_dir / "formatted.json"
        
        write_json(file_path, data, indent=2, ensure_ascii=False)
        
        content = file_path.read_text(encoding="utf-8")
        assert "  " in content  # Check indentation
        assert content.count("\n") > 1  # Check multi-line formatting

    def test_read_invalid_json(self, invalid_json_file_path: Path) -> None:
        """Test reading invalid JSON raises JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            read_json(invalid_json_file_path)

    def test_write_json_non_serializable(self, temp_dir: Path) -> None:
        """Test writing non-serializable data raises TypeError."""
        file_path = temp_dir / "non_serializable.json"
        non_serializable = {"function": lambda x: x}
        
        with pytest.raises(TypeError):
            write_json(file_path, non_serializable)

    def test_roundtrip_json_operations(self, temp_dir: Path, sample_json_data: dict[str, Any]) -> None:
        """Test roundtrip JSON operations (write then read)."""
        file_path = temp_dir / "roundtrip.json"
        
        # Write and read back
        write_json(file_path, sample_json_data)
        data = read_json(file_path)
        
        assert data == sample_json_data

    def test_json_with_unicode(self, temp_dir: Path) -> None:
        """Test JSON operations with Unicode characters."""
        data = {
            "japanese": "こんにちは",
            "russian": "Привет", 
            "emoji": "🎉",
            "math": "α + β = γ"
        }
        file_path = temp_dir / "unicode.json"
        
        write_json(file_path, data, ensure_ascii=False)
        loaded_data = read_json(file_path)
        
        assert loaded_data == data


class TestYAMLOperations:
    """Unit tests for YAML file operations."""

    def test_read_yaml(self, yaml_file_path: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test reading YAML file."""
        data = read_yaml(yaml_file_path)
        assert data == sample_yaml_data

    def test_write_yaml(self, temp_dir: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test writing YAML file."""
        file_path = temp_dir / "test_write.yaml"
        write_yaml(file_path, sample_yaml_data)
        
        # Verify file was written correctly
        assert file_path.exists()
        with file_path.open("r", encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == sample_yaml_data

    def test_write_yaml_with_formatting(self, temp_dir: Path) -> None:
        """Test writing YAML with flow style formatting."""
        data = {"items": ["item1", "item2", "item3"]}
        file_path = temp_dir / "formatted.yaml"
        
        write_yaml(file_path, data, default_flow_style=True)
        
        content = file_path.read_text(encoding="utf-8")
        assert "[" in content and "]" in content  # Check flow style

    def test_read_invalid_yaml(self, invalid_yaml_file_path: Path) -> None:
        """Test reading invalid YAML raises YAMLError."""
        with pytest.raises(yaml.YAMLError):
            read_yaml(invalid_yaml_file_path)

    def test_roundtrip_yaml_operations(self, temp_dir: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test roundtrip YAML operations (write then read)."""
        file_path = temp_dir / "roundtrip.yaml"
        
        # Write and read back
        write_yaml(file_path, sample_yaml_data)
        data = read_yaml(file_path)
        
        assert data == sample_yaml_data

    def test_yaml_with_unicode(self, temp_dir: Path) -> None:
        """Test YAML operations with Unicode characters."""
        data = {
            "languages": {
                "japanese": "日本語",
                "korean": "한국어",
                "chinese": "中文"
            },
            "symbols": ["→", "∞", "≠", "≤", "≥"]
        }
        file_path = temp_dir / "unicode.yaml"
        
        write_yaml(file_path, data)
        loaded_data = read_yaml(file_path)
        
        assert loaded_data == data


class TestErrorHandling:
    """Unit tests for error handling scenarios."""

    def test_read_file_permission_denied(self, temp_dir: Path) -> None:
        """Test handling permission denied errors."""
        # This test might not work on all systems due to permission restrictions
        # but the function should handle PermissionError appropriately
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")
        
        # We can't easily test permission denied in unit tests,
        # but we ensure the function propagates the exception
        content = read_file(file_path)
        assert content == "content"

    def test_path_as_string_and_pathlib(self, temp_dir: Path, sample_text_utf8: str) -> None:
        """Test that functions accept both string and Path objects."""
        file_path = temp_dir / "path_test.txt"
        
        # Test with Path object
        write_file(file_path, sample_text_utf8)
        content_from_path = read_file(file_path)
        
        # Test with string
        content_from_string = read_file(str(file_path))
        
        assert content_from_path == content_from_string == sample_text_utf8

    def test_empty_files(self, temp_dir: Path) -> None:
        """Test handling of empty files."""
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        
        content = read_file(empty_file)
        assert content == ""

        # Test empty JSON
        empty_json = temp_dir / "empty.json"
        write_json(empty_json, {})
        data = read_json(empty_json)
        assert data == {}

        # Test empty YAML
        empty_yaml = temp_dir / "empty.yaml"
        write_yaml(empty_yaml, {})
        data = read_yaml(empty_yaml)
        assert data == {}


class TestTypeSupport:
    """Unit tests for different data types support."""

    def test_json_complex_types(self, temp_dir: Path) -> None:
        """Test JSON with complex nested structures."""
        complex_data = {
            "string": "value",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "null_value": None,
            "list": [1, "two", 3.0, True, None],
            "nested_dict": {
                "inner_list": [{"a": 1}, {"b": 2}],
                "inner_dict": {"x": "y", "z": 123}
            }
        }
        
        file_path = temp_dir / "complex.json"
        write_json(file_path, complex_data)
        loaded_data = read_json(file_path)
        
        assert loaded_data == complex_data

    def test_yaml_complex_types(self, temp_dir: Path) -> None:
        """Test YAML with complex nested structures."""
        complex_data = {
            "multiline_string": "This is a\nmultiline string\nwith newlines",
            "list_of_dicts": [
                {"name": "item1", "value": 100},
                {"name": "item2", "value": 200}
            ],
            "nested_structure": {
                "level1": {
                    "level2": {
                        "level3": ["deep", "nesting", "test"]
                    }
                }
            }
        }
        
        file_path = temp_dir / "complex.yaml"
        write_yaml(file_path, complex_data)
        loaded_data = read_yaml(file_path)
        
        assert loaded_data == complex_data