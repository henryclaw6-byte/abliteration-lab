#!/usr/bin/env python3
"""
config_manager.py
Henry, Qwen & Codex — Configuration Management

Centralized configuration management for Abliteration Lab.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Config:
    """Configuration dataclass."""
    # Model settings
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    device: str = "auto"
    
    # Experiment settings
    n_samples: int = 32
    layer_of_interest: int = 18
    layers_to_check: str = "resid_pre"
    
    # Output settings
    output_dir: str = "experiment_results"
    save_model: bool = True
    generate_dashboard: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "abliteration.log"
    verbose: bool = False
    
    # Paths
    memory_dir: str = "memory"
    handoff_dir: str = "memory/handoffs"
    artifacts_dir: str = "artifacts"
    
    # Triple Alliance
    agent_name: str = "henry"
    enable_collaboration: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, filepath: str):
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create from dictionary."""
        # Filter only valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)
    
    @classmethod
    def load(cls, filepath: str) -> 'Config':
        """Load from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        return cls.from_dict(data)


class ConfigManager:
    """Manager for loading and saving configurations."""
    
    DEFAULT_CONFIG_PATH = "config.json"
    ENV_PREFIX = "ABLITERATION_"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = Config()
        self._load()
    
    def _load(self):
        """Load configuration from file and environment."""
        # Load from file if exists
        if Path(self.config_path).exists():
            try:
                self.config = Config.load(self.config_path)
            except Exception as e:
                print(f"⚠️ Could not load config: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            f"{self.ENV_PREFIX}MODEL_NAME": "model_name",
            f"{self.ENV_PREFIX}DEVICE": "device",
            f"{self.ENV_PREFIX}OUTPUT_DIR": "output_dir",
            f"{self.ENV_PREFIX}LOG_LEVEL": "log_level",
            f"{self.ENV_PREFIX}AGENT_NAME": "agent_name",
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                setattr(self.config, config_key, value)
    
    def save(self):
        """Save current configuration to file."""
        self.config.save(self.config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            raise KeyError(f"Unknown config key: {key}")
    
    def ensure_directories(self):
        """Create necessary directories."""
        dirs = [
            self.config.output_dir,
            self.config.memory_dir,
            self.config.handoff_dir,
            self.config.artifacts_dir
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def print_config(self):
        """Print current configuration."""
        print("\n" + "=" * 60)
        print("CURRENT CONFIGURATION")
        print("=" * 60)
        
        for key, value in self.config.to_dict().items():
            print(f"{key:20s}: {value}")
        
        print("=" * 60)


def main():
    """CLI for configuration management."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Abliteration Lab Config Manager')
    parser.add_argument('--init', action='store_true', help='Initialize default config')
    parser.add_argument('--show', action='store_true', help='Show current config')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set config value')
    parser.add_argument('--get', metavar='KEY', help='Get config value')
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.init:
        manager.save()
        manager.ensure_directories()
        print(f"✅ Configuration initialized: {manager.config_path}")
        print("✅ Directories created")
    
    elif args.show:
        manager.print_config()
    
    elif args.set:
        key, value = args.set
        manager.set(key, value)
        manager.save()
        print(f"✅ Set {key} = {value}")
    
    elif args.get:
        value = manager.get(args.get)
        print(value)
    
    else:
        manager.print_config()


if __name__ == "__main__":
    main()
