"""Generic file handler with support for various encodings and formats.

This module provides utility functions for file operations with support for:
- Generic file read/write with encoding support (UTF-8, CP932)
- JSON file operations with proper error handling
- YAML file operations with proper error handling
- Automatic directory creation for write operations
"""

import json
from pathlib import Path
from typing import Any

import yaml


def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read text file with specified encoding.
    
    Args:
        path: File path to read from
        encoding: Text encoding to use (default: utf-8)
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file does not exist
        UnicodeDecodeError: If file cannot be decoded with specified encoding
        PermissionError: If file cannot be read due to permissions
    """
    file_path = Path(path)
    
    with file_path.open("r", encoding=encoding) as f:
        return f.read()


def write_file(
    path: str | Path, 
    content: str, 
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> None:
    """Write text file with specified encoding.
    
    Args:
        path: File path to write to
        content: Text content to write
        encoding: Text encoding to use (default: utf-8)
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        PermissionError: If file cannot be written due to permissions
        UnicodeEncodeError: If content cannot be encoded with specified encoding
        OSError: If other I/O error occurs
    """
    file_path = Path(path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open("w", encoding=encoding) as f:
        f.write(content)


def read_json(path: str | Path) -> Any:
    """Read JSON file and return Python object.
    
    Args:
        path: File path to read from
        
    Returns:
        Parsed JSON data as Python object
        
    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file contains invalid JSON
        PermissionError: If file cannot be read due to permissions
    """
    file_path = Path(path)
    
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(
    path: str | Path, 
    data: Any, 
    indent: int | None = 4,
    create_dirs: bool = True
) -> None:
    """Write Python object to JSON file.
    
    Args:
        path: File path to write to
        data: Python object to serialize to JSON
        indent: Number of spaces for indentation (None for compact format)
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        TypeError: If data cannot be serialized to JSON
        PermissionError: If file cannot be written due to permissions
        OSError: If other I/O error occurs
    """
    file_path = Path(path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_yaml(path: str | Path) -> Any:
    """Read YAML file and return Python object.
    
    Args:
        path: File path to read from
        
    Returns:
        Parsed YAML data as Python object
        
    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If file contains invalid YAML
        PermissionError: If file cannot be read due to permissions
    """
    file_path = Path(path)
    
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(
    path: str | Path, 
    data: Any,
    create_dirs: bool = True
) -> None:
    """Write Python object to YAML file.
    
    Args:
        path: File path to write to
        data: Python object to serialize to YAML
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        yaml.YAMLError: If data cannot be serialized to YAML
        PermissionError: If file cannot be written due to permissions
        OSError: If other I/O error occurs
    """
    file_path = Path(path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data, 
            f, 
            default_flow_style=False,
            allow_unicode=True,
            indent=2
        )