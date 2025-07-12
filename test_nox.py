#!/usr/bin/env python3
"""Quick test to verify nox commands work."""

import subprocess
import sys

def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main() -> None:
    """Main function to test nox commands."""
    commands = [
        ["nox", "-s", "lint"],
        ["nox", "-s", "typing"], 
        ["nox", "-s", "test_unit"]
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        exit_code, stdout, stderr = run_command(cmd)
        print(f"Exit code: {exit_code}")
        
        if stdout:
            print("STDOUT:")
            print(stdout)
        
        if stderr:
            print("STDERR:")
            print(stderr)
        
        print("-" * 50)
        
        if exit_code != 0:
            print(f"Command failed: {' '.join(cmd)}")
            return
    
    print("All commands completed successfully!")

if __name__ == "__main__":
    main()