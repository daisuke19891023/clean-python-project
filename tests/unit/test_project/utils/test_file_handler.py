"""Unit tests for file_handler module."""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

from test_project.utils.file_handler import (
    read_file,
    read_json,
    read_yaml,
    write_file,
    write_json,
    write_yaml,
)


class TestGenericFileOperations:
    """Test generic file read/write operations with encoding support."""

    def test_read_file_utf8(
        self, sample_utf8_file: Path, sample_text_utf8: str
    ) -> None:
        """Test reading UTF-8 encoded file."""
        content = read_file(sample_utf8_file, encoding="utf-8")
        assert content == sample_text_utf8

    def test_read_file_cp932(self, sample_text_cp932: str) -> None:
        """Test reading CP932 encoded file."""
        # Create a temporary file with CP932 encoding
        with tempfile.NamedTemporaryFile(mode="w", encoding="cp932", delete=False) as f:
            f.write(sample_text_cp932)
            temp_path = Path(f.name)

        try:
            content = read_file(temp_path, encoding="cp932")
            assert content == sample_text_cp932
        finally:
            temp_path.unlink()

    def test_write_file_utf8(self, temp_file_path: Path, sample_text_utf8: str) -> None:
        """Test writing UTF-8 encoded file."""
        write_file(temp_file_path, sample_text_utf8, encoding="utf-8")
        
        # Verify the file was written correctly
        with temp_file_path.open(encoding="utf-8") as f:
            content = f.read()
        assert content == sample_text_utf8
        
        # Clean up
        temp_file_path.unlink()

    def test_write_file_cp932(self, temp_file_path: Path, sample_text_cp932: str) -> None:
        """Test writing CP932 encoded file."""
        write_file(temp_file_path, sample_text_cp932, encoding="cp932")
        
        # Verify the file was written correctly
        with temp_file_path.open(encoding="cp932") as f:
            content = f.read()
        assert content == sample_text_cp932
        
        # Clean up
        temp_file_path.unlink()

    def test_read_file_not_found(self) -> None:
        """Test reading non-existent file raises FileNotFoundError."""
        non_existent_path = Path("/non/existent/file.txt")
        
        with pytest.raises(FileNotFoundError):
            read_file(non_existent_path)

    def test_read_file_encoding_error(self, sample_utf8_file: Path) -> None:
        """Test reading UTF-8 file with wrong encoding raises UnicodeDecodeError."""
        with pytest.raises(UnicodeDecodeError):
            read_file(sample_utf8_file, encoding="ascii")

    def test_write_file_directory_not_exists(self, sample_text_utf8: str) -> None:
        """Test writing to non-existent directory creates directories."""
        temp_dir = Path(tempfile.mkdtemp())
        nested_path = temp_dir / "nested" / "dir" / "file.txt"
        
        write_file(nested_path, sample_text_utf8)
        
        # Verify file was created
        assert nested_path.exists()
        assert nested_path.read_text(encoding="utf-8") == sample_text_utf8
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


class TestJSONOperations:
    """Test JSON-specific file operations."""

    def test_read_json_valid(self, sample_json_file: Path, sample_json_data: dict[str, Any]) -> None:
        """Test reading valid JSON file."""
        data = read_json(sample_json_file)
        assert data == sample_json_data

    def test_read_json_invalid(self) -> None:
        """Test reading invalid JSON file raises JSONDecodeError."""
        # Create a file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json content}')
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(json.JSONDecodeError):
                read_json(temp_path)
        finally:
            temp_path.unlink()

    def test_write_json(self, temp_file_path: Path, sample_json_data: dict[str, Any]) -> None:
        """Test writing JSON file with proper formatting."""
        json_path = temp_file_path.with_suffix(".json")
        
        write_json(json_path, sample_json_data, indent=4)
        
        # Verify the file was written correctly
        with json_path.open(encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data == sample_json_data
        
        # Verify formatting (should be indented)
        content = json_path.read_text(encoding="utf-8")
        assert "\n" in content  # Should contain newlines for indentation
        
        # Clean up
        json_path.unlink()

    def test_write_json_no_indent(self, temp_file_path: Path) -> None:
        """Test writing JSON file without indentation."""
        json_path = temp_file_path.with_suffix(".json")
        test_data = {"compact": True, "value": 123}
        
        write_json(json_path, test_data, indent=None)
        
        # Verify compact format
        content = json_path.read_text(encoding="utf-8")
        assert content == '{"compact": true, "value": 123}'
        
        # Clean up
        json_path.unlink()

    def test_read_json_file_not_found(self) -> None:
        """Test reading non-existent JSON file raises FileNotFoundError."""
        non_existent_path = Path("/non/existent/file.json")
        
        with pytest.raises(FileNotFoundError):
            read_json(non_existent_path)

    def test_json_roundtrip(self, temp_file_path: Path, sample_json_data: dict[str, Any]) -> None:
        """Test writing then reading JSON file maintains data integrity."""
        json_path = temp_file_path.with_suffix(".json")
        
        # Write then read
        write_json(json_path, sample_json_data)
        loaded_data = read_json(json_path)
        
        assert loaded_data == sample_json_data
        
        # Clean up
        json_path.unlink()


class TestYAMLOperations:
    """Test YAML-specific file operations."""

    def test_read_yaml_valid(self, sample_yaml_file: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test reading valid YAML file."""
        data = read_yaml(sample_yaml_file)
        assert data == sample_yaml_data

    def test_read_yaml_invalid(self) -> None:
        """Test reading invalid YAML file raises YAMLError."""
        # Create a file with invalid YAML
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(yaml.YAMLError):
                read_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_write_yaml(self, temp_file_path: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test writing YAML file with proper formatting."""
        yaml_path = temp_file_path.with_suffix(".yaml")
        
        write_yaml(yaml_path, sample_yaml_data)
        
        # Verify the file was written correctly
        with yaml_path.open(encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == sample_yaml_data
        
        # Clean up
        yaml_path.unlink()

    def test_read_yaml_file_not_found(self) -> None:
        """Test reading non-existent YAML file raises FileNotFoundError."""
        non_existent_path = Path("/non/existent/file.yaml")
        
        with pytest.raises(FileNotFoundError):
            read_yaml(non_existent_path)

    def test_yaml_roundtrip(self, temp_file_path: Path, sample_yaml_data: dict[str, Any]) -> None:
        """Test writing then reading YAML file maintains data integrity."""
        yaml_path = temp_file_path.with_suffix(".yaml")
        
        # Write then read
        write_yaml(yaml_path, sample_yaml_data)
        loaded_data = read_yaml(yaml_path)
        
        assert loaded_data == sample_yaml_data
        
        # Clean up
        yaml_path.unlink()


class TestEncodingRoundtrip:
    """Test encoding roundtrip operations."""

    def test_utf8_roundtrip(self, temp_file_path: Path, sample_text_utf8: str) -> None:
        """Test UTF-8 encoding roundtrip maintains data integrity."""
        write_file(temp_file_path, sample_text_utf8, encoding="utf-8")
        content = read_file(temp_file_path, encoding="utf-8")
        
        assert content == sample_text_utf8
        
        # Clean up
        temp_file_path.unlink()

    def test_cp932_roundtrip(self, temp_file_path: Path, sample_text_cp932: str) -> None:
        """Test CP932 encoding roundtrip maintains data integrity."""
        write_file(temp_file_path, sample_text_cp932, encoding="cp932")
        content = read_file(temp_file_path, encoding="cp932")
        
        assert content == sample_text_cp932
        
        # Clean up
        temp_file_path.unlink()


class TestCompleteWorkflow:
    """Test complete file operations workflow (E2E style)."""

    def test_complete_file_operations_workflow(self, temp_file_path: Path) -> None:
        """Test complete workflow using all file handler functions."""
        # Test data
        text_data = "テスト用のUTF-8テキストデータ"
        json_data = {"name": "テスト", "value": 42, "active": True}
        yaml_data = {"title": "YAMLテスト", "items": ["item1", "item2"], "count": 2}
        
        # Create file paths
        text_path = temp_file_path.with_suffix(".txt")
        json_path = temp_file_path.with_suffix(".json") 
        yaml_path = temp_file_path.with_suffix(".yaml")
        
        try:
            # 1. Write text file with UTF-8 encoding
            write_file(text_path, text_data, encoding="utf-8")
            
            # 2. Write JSON file
            write_json(json_path, json_data, indent=2)
            
            # 3. Write YAML file
            write_yaml(yaml_path, yaml_data)
            
            # 4. Read all files back and verify
            read_text = read_file(text_path, encoding="utf-8")
            read_json_data = read_json(json_path)
            read_yaml_data = read_yaml(yaml_path)
            
            # 5. Assert all data integrity
            assert read_text == text_data
            assert read_json_data == json_data
            assert read_yaml_data == yaml_data
            
            # 6. Verify files exist
            assert text_path.exists()
            assert json_path.exists()
            assert yaml_path.exists()
            
        finally:
            # Clean up all files
            for path in [text_path, json_path, yaml_path]:
                if path.exists():
                    path.unlink()


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    def test_write_to_readonly_directory(self, sample_text_utf8: str) -> None:
        """Test writing to read-only directory handles permissions gracefully."""
        # This test may vary by platform, but should handle permission errors
        readonly_path = Path("/readonly/path/file.txt")
        
        with pytest.raises((PermissionError, OSError)):
            write_file(readonly_path, sample_text_utf8)

    def test_invalid_encoding_parameter(self, temp_file_path: Path) -> None:
        """Test invalid encoding parameter raises appropriate error."""
        with pytest.raises((LookupError, ValueError)):
            write_file(temp_file_path, "test", encoding="invalid_encoding")

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_permission_error_handling(self, mock_open: Any) -> None:
        """Test permission error is properly raised."""
        test_path = Path("test_file.txt")
        
        with pytest.raises(PermissionError):
            read_file(test_path)