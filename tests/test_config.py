import pytest
import yaml
from pathlib import Path
from scripts.config import load_config, Config


def test_load_config_from_yaml(tmp_path):
    """Test loading config from YAML file."""
    config_data = {
        "model": {
            "base_url": "https://integrate.api.nvidia.com/v1",
            "api_key": "nvapi-xxxx",
            "model_name": "meta/llama-3.1-8b-instruct"
        },
        "sources": {
            "arxiv": {"enabled": True},
            "semantic_scholar": {"enabled": True, "api_key": ""},
            "google_scholar": {"enabled": False, "serpapi_key": ""}
        },
        "dimensions": [
            {"name": "relevance", "description": "与搜索策略的相关程度"}
        ],
        "search": {
            "max_results_per_source": 30,
            "date_range_years": 3,
            "concurrent_requests": 5,
            "dedup_threshold": 0.85
        }
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    config = load_config(str(config_file))

    assert config.model.base_url == "https://integrate.api.nvidia.com/v1"
    assert config.model.api_key == "nvapi-xxxx"
    assert config.sources.arxiv.enabled is True
    assert config.sources.google_scholar.enabled is False
    assert len(config.dimensions) == 1
    assert config.search.max_results_per_source == 30


def test_config_defaults():
    """Test default config values."""
    config = Config()
    assert config.search.concurrent_requests == 5
    assert config.search.dedup_threshold == 0.85
