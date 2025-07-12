"""Generic file handler with JSON/YAML support and logging integration.

This module provides comprehensive file operations with support for multiple encodings,
JSON/YAML parsing, and structured error logging using the logger module.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from test_project.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read file content with specified encoding.

    Args:
        path: File path to read
        encoding: File encoding ('utf-8' or 'cp932')

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no read permission
        UnicodeDecodeError: If encoding is incompatible
    """
    file_path = Path(path)
    
    try:
        logger.debug("Reading file", path=str(file_path), encoding=encoding)
        content = file_path.read_text(encoding=encoding)
        logger.info("File read successfully", path=str(file_path), size=len(content))
        return content
        
    except FileNotFoundError as e:
        logger.error("File not found", path=str(file_path), error=str(e))
        raise
        
    except PermissionError as e:
        logger.error("Permission denied reading file", path=str(file_path), error=str(e))
        raise
        
    except UnicodeDecodeError as e:
        logger.error("Encoding error reading file", path=str(file_path), encoding=encoding, error=str(e))
        raise


def write_file(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """Write content to file with specified encoding.

    Args:
        path: File path to write
        content: Content to write
        encoding: File encoding ('utf-8' or 'cp932')

    Raises:
        PermissionError: If no write permission
        UnicodeEncodeError: If encoding is incompatible
    """
    file_path = Path(path)
    
    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Writing file", path=str(file_path), encoding=encoding, size=len(content))
        file_path.write_text(content, encoding=encoding)
        logger.info("File written successfully", path=str(file_path), size=len(content))
        
    except PermissionError as e:
        logger.error("Permission denied writing file", path=str(file_path), error=str(e))
        raise
        
    except UnicodeEncodeError as e:
        logger.error("Encoding error writing file", path=str(file_path), encoding=encoding, error=str(e))
        raise


def read_json(path: str | Path) -> Any:
    """Read JSON file and return parsed data.

    Args:
        path: JSON file path

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no read permission
        json.JSONDecodeError: If JSON is malformed
    """
    file_path = Path(path)
    
    try:
        logger.debug("Reading JSON file", path=str(file_path))
        content = read_file(file_path, encoding="utf-8")
        data = json.loads(content)
        logger.info("JSON file parsed successfully", path=str(file_path), type=type(data).__name__)
        return data
        
    except json.JSONDecodeError as e:
        logger.error("JSON decode error", path=str(file_path), error=str(e), line=e.lineno, column=e.colno)
        raise


def write_json(path: str | Path, data: Any, indent: int = 4, ensure_ascii: bool = False) -> None:
    """Write data to JSON file with formatting.

    Args:
        path: JSON file path
        data: Data to serialize
        indent: JSON indentation
        ensure_ascii: Whether to escape non-ASCII characters

    Raises:
        PermissionError: If no write permission
        TypeError: If data is not JSON serializable
    """
    file_path = Path(path)
    
    try:
        logger.debug("Writing JSON file", path=str(file_path), data_type=type(data).__name__)
        json_content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        write_file(file_path, json_content, encoding="utf-8")
        logger.info("JSON file written successfully", path=str(file_path))
        
    except TypeError as e:
        logger.error("JSON serialization error", path=str(file_path), data_type=type(data).__name__, error=str(e))
        raise


def read_yaml(path: str | Path) -> Any:
    """Read YAML file and return parsed data.

    Args:
        path: YAML file path

    Returns:
        Parsed YAML data

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no read permission
        yaml.YAMLError: If YAML is malformed
    """
    file_path = Path(path)
    
    try:
        logger.debug("Reading YAML file", path=str(file_path))
        content = read_file(file_path, encoding="utf-8")
        data = yaml.safe_load(content)
        logger.info("YAML file parsed successfully", path=str(file_path), type=type(data).__name__)
        return data
        
    except yaml.YAMLError as e:
        logger.error("YAML parse error", path=str(file_path), error=str(e))
        raise


def write_yaml(path: str | Path, data: Any, default_flow_style: bool = False) -> None:
    """Write data to YAML file with formatting.

    Args:
        path: YAML file path
        data: Data to serialize
        default_flow_style: Whether to use flow style formatting

    Raises:
        PermissionError: If no write permission
        yaml.YAMLError: If data cannot be serialized to YAML
    """
    file_path = Path(path)
    
    try:
        logger.debug("Writing YAML file", path=str(file_path), data_type=type(data).__name__)
        yaml_content = yaml.dump(
            data, 
            default_flow_style=default_flow_style, 
            allow_unicode=True,
            indent=2
        )
        write_file(file_path, yaml_content, encoding="utf-8")
        logger.info("YAML file written successfully", path=str(file_path))
        
    except yaml.YAMLError as e:
        logger.error("YAML serialization error", path=str(file_path), data_type=type(data).__name__, error=str(e))
        raise