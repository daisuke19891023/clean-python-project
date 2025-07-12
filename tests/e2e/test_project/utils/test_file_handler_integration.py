"""E2E tests for file_handler and logger integration."""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from test_project.utils.file_handler import (
    read_file,
    write_file,
    read_json,
    write_json,
    read_yaml,
    write_yaml,
)
from test_project.utils.logger import configure_logging, get_logger


class TestFileHandlerLoggingIntegration:
    """Complete workflow tests for file_handler with logging integration."""

    def test_complete_file_operations_with_logging(
        self, 
        temp_dir: Path, 
        sample_json_data: dict[str, Any],
        sample_yaml_data: dict[str, Any]
    ) -> None:
        """Complete workflow test combining file operations with structured logging."""
        # Set up logging to capture all operations
        log_file = temp_dir / "operations.log"
        configure_logging(
            log_level="DEBUG",
            log_format="json", 
            log_file=str(log_file)
        )
        
        logger = get_logger("file_operations_test")
        logger.info("Starting complete file operations workflow")
        
        # Test 1: JSON file operations
        json_file = temp_dir / "workflow.json"
        write_json(json_file, sample_json_data)
        loaded_json = read_json(json_file)
        assert loaded_json == sample_json_data
        
        # Test 2: YAML file operations  
        yaml_file = temp_dir / "workflow.yaml"
        write_yaml(yaml_file, sample_yaml_data)
        loaded_yaml = read_yaml(yaml_file)
        assert loaded_yaml == sample_yaml_data
        
        # Test 3: Text file operations with different encodings
        text_utf8 = "UTF-8 test: こんにちは 🎉"
        text_cp932 = "CP932テスト"
        
        utf8_file = temp_dir / "text_utf8.txt"
        cp932_file = temp_dir / "text_cp932.txt"
        
        write_file(utf8_file, text_utf8, encoding="utf-8")
        write_file(cp932_file, text_cp932, encoding="cp932")
        
        loaded_utf8 = read_file(utf8_file, encoding="utf-8")
        loaded_cp932 = read_file(cp932_file, encoding="cp932")
        
        assert loaded_utf8 == text_utf8
        assert loaded_cp932 == text_cp932
        
        logger.info("File operations workflow completed successfully")
        
        # Verify that log file contains structured entries for all operations
        assert log_file.exists()
        log_content = log_file.read_text()
        log_lines = [line for line in log_content.strip().split("\n") if line]
        
        # Should have multiple log entries from file operations
        assert len(log_lines) >= 10
        
        # Parse and verify log structure
        for line in log_lines:
            log_entry: dict[str, Any] = json.loads(line)
            assert "timestamp" in log_entry
            assert "level" in log_entry
            assert "event" in log_entry
            assert "logger" in log_entry

    def test_error_handling_with_logging(self, temp_dir: Path) -> None:
        """Test error scenarios with comprehensive logging."""
        # Set up logging to capture errors
        log_file = temp_dir / "errors.log"
        configure_logging(
            log_level="ERROR",
            log_format="json",
            log_file=str(log_file)
        )
        
        # Test 1: File not found error
        non_existent = temp_dir / "does_not_exist.json"
        with pytest.raises(FileNotFoundError):
            read_json(non_existent)
        
        # Test 2: JSON decode error
        invalid_json = temp_dir / "invalid.json"
        invalid_json.write_text('{"invalid": json}', encoding="utf-8")
        
        with pytest.raises(json.JSONDecodeError):
            read_json(invalid_json)
        
        # Test 3: Encoding error
        cp932_content = "日本語テスト"
        cp932_file = temp_dir / "cp932.txt"
        cp932_file.write_text(cp932_content, encoding="cp932")
        
        with pytest.raises(UnicodeDecodeError):
            read_file(cp932_file, encoding="utf-8")
        
        # Verify error logs were created
        assert log_file.exists()
        log_content = log_file.read_text()
        log_lines = [line for line in log_content.strip().split("\n") if line]
        
        # Should have error entries for each failed operation
        error_logs = []
        for line in log_lines:
            log_entry: dict[str, Any] = json.loads(line)
            if log_entry.get("level") == "error":
                error_logs.append(log_entry)
        
        assert len(error_logs) >= 3
        
        # Verify error details are logged
        error_types = [log.get("event", "") for log in error_logs]
        assert any("not found" in error.lower() for error in error_types)
        assert any("decode error" in error.lower() for error in error_types)
        assert any("encoding error" in error.lower() for error in error_types)

    def test_performance_logging_integration(self, temp_dir: Path) -> None:
        """Test file operations with performance logging."""
        from test_project.utils.logger import log_performance
        
        # Set up logging
        log_file = temp_dir / "performance.log"
        configure_logging(
            log_level="INFO",
            log_format="json",
            log_file=str(log_file)
        )
        
        logger = get_logger("performance_test")
        
        # Create performance-logged file operations
        @log_performance(logger)
        def batch_file_operations() -> dict[str, Any]:
            """Perform multiple file operations for performance testing."""
            data = {"batch": "operations", "count": 100}
            
            for i in range(5):
                json_file = temp_dir / f"batch_{i}.json"
                yaml_file = temp_dir / f"batch_{i}.yaml"
                
                write_json(json_file, data)
                write_yaml(yaml_file, data)
                
                read_json(json_file)
                read_yaml(yaml_file)
            
            return data
        
        # Execute the performance-logged function
        result = batch_file_operations()
        assert result["batch"] == "operations"
        
        # Verify performance logging
        assert log_file.exists()
        log_content = log_file.read_text()
        log_lines = [line for line in log_content.strip().split("\n") if line]
        
        # Find performance log entry
        performance_logs = []
        for line in log_lines:
            log_entry: dict[str, Any] = json.loads(line)
            if "duration_ms" in log_entry and "function_name" in log_entry:
                performance_logs.append(log_entry)
        
        assert len(performance_logs) >= 1
        perf_log = performance_logs[0]
        assert perf_log["function_name"] == "batch_file_operations"
        assert isinstance(perf_log["duration_ms"], (int, float))
        assert perf_log["duration_ms"] >= 0

    def test_structured_data_workflow_with_context_logging(
        self, 
        temp_dir: Path
    ) -> None:
        """Test complete data processing workflow with context logging."""
        # Set up logging with context
        log_file = temp_dir / "workflow.log"
        configure_logging(
            log_level="INFO",
            log_format="json",
            log_file=str(log_file)
        )
        
        # Create context-bound logger
        logger = get_logger("data_workflow")
        workflow_logger = logger.bind(
            workflow_id="wf_001",
            user_id="user_123",
            session_id="sess_456"
        )
        
        workflow_logger.info("Starting data processing workflow")
        
        # Step 1: Create source data
        source_data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "user"}
            ],
            "settings": {
                "version": "1.0",
                "environment": "production",
                "debug": False
            }
        }
        
        # Step 2: Save as JSON
        json_source = temp_dir / "source_data.json"
        write_json(json_source, source_data, indent=2)
        workflow_logger.info("Source data saved", format="json", file=str(json_source))
        
        # Step 3: Load and transform to YAML
        loaded_data = read_json(json_source)
        yaml_output = temp_dir / "transformed_data.yaml"
        write_yaml(yaml_output, loaded_data)
        workflow_logger.info("Data transformed", format="yaml", file=str(yaml_output))
        
        # Step 4: Create summary file
        summary = {
            "total_users": len(loaded_data["users"]),
            "admin_count": sum(1 for u in loaded_data["users"] if u["role"] == "admin"),
            "user_count": sum(1 for u in loaded_data["users"] if u["role"] == "user"),
            "settings_version": loaded_data["settings"]["version"]
        }
        
        summary_file = temp_dir / "summary.json"
        write_json(summary_file, summary)
        workflow_logger.info(
            "Workflow completed", 
            total_users=summary["total_users"],
            admin_count=summary["admin_count"],
            files_created=3
        )
        
        # Verify all files exist
        assert json_source.exists()
        assert yaml_output.exists() 
        assert summary_file.exists()
        
        # Verify data integrity
        final_yaml_data = read_yaml(yaml_output)
        final_summary = read_json(summary_file)
        
        assert final_yaml_data == source_data
        assert final_summary["total_users"] == 3
        assert final_summary["admin_count"] == 1
        
        # Verify structured logging with context
        assert log_file.exists()
        log_content = log_file.read_text()
        log_lines = [line for line in log_content.strip().split("\n") if line]
        
        workflow_logs = []
        for line in log_lines:
            log_entry: dict[str, Any] = json.loads(line)
            if "workflow_id" in log_entry:
                workflow_logs.append(log_entry)
        
        # Should have workflow logs with context
        assert len(workflow_logs) >= 4
        
        for log_entry in workflow_logs:
            assert log_entry["workflow_id"] == "wf_001"
            assert log_entry["user_id"] == "user_123"
            assert log_entry["session_id"] == "sess_456"

    def test_cross_module_error_propagation(self, temp_dir: Path) -> None:
        """Test error propagation between file_handler and logger modules."""
        # Set up logging to capture the full error chain
        log_file = temp_dir / "error_propagation.log"
        configure_logging(
            log_level="DEBUG",
            log_format="json",
            log_file=str(log_file), 
            include_caller=True
        )
        
        logger = get_logger("error_test")
        
        # Test scenario: Try to read a file that will cause encoding errors
        logger.info("Testing error propagation between modules")
        
        # Create a file with mixed encoding issues
        mixed_encoding_file = temp_dir / "mixed_encoding.txt"
        # Write with one encoding
        mixed_encoding_file.write_bytes(
            "正常なテキスト".encode("cp932") + b"\xFF\xFE" + "Invalid".encode("utf-8")
        )
        
        # Try to read with different encoding to trigger error
        try:
            content = read_file(mixed_encoding_file, encoding="utf-8")
            # This shouldn't execute due to encoding error
            pytest.fail("Expected UnicodeDecodeError")
        except UnicodeDecodeError as e:
            logger.error(
                "Cross-module error handled",
                error_type=type(e).__name__,
                error_message=str(e),
                module="file_handler"
            )
        
        # Verify comprehensive error logging
        assert log_file.exists()
        log_content = log_file.read_text()
        log_lines = [line for line in log_content.strip().split("\n") if line]
        
        # Should have error logs from both modules
        error_logs = []
        for line in log_lines:
            log_entry: dict[str, Any] = json.loads(line)
            if log_entry.get("level") == "error":
                error_logs.append(log_entry)
        
        assert len(error_logs) >= 2  # One from file_handler, one from test
        
        # Verify caller information is included
        file_handler_errors = [
            log for log in error_logs 
            if "file_handler" in log.get("logger", "")
        ]
        assert len(file_handler_errors) >= 1
        
        # Verify error details
        for error_log in file_handler_errors:
            assert "caller" in error_log
            assert "filename" in error_log["caller"]
            assert "function" in error_log["caller"]
            assert "line" in error_log["caller"]