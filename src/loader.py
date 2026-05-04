# src/loader.py

"""
Loading prompt from YAML file.

YAML prompts provide flexibility, portability, version control, and multi-agent orchestration.
For prompt portability across different environments & LLM models.
"""

import yaml
from pathlib import Path

def load_prompt(version: str = "v1"):
    """
    Loads the system prompt from a versioned YAML file.
    """
    project_root = Path(__file__).parent.parent
    file_path = project_root / "config" / "prompts" / f"analyst_{version}.yaml"
    
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config["system_prompt"]

if __name__ == "__main__":
    # Test the loader
    print("--- Loaded System Prompt ---")
    print(load_prompt())