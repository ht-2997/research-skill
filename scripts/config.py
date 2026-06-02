import os
from dataclasses import dataclass, field
from typing import List, Optional
import yaml


@dataclass
class ModelConfig:
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str = ""
    model_name: str = "openai/gpt-4o"


@dataclass
class ArxivConfig:
    enabled: bool = True


@dataclass
class SemanticScholarConfig:
    enabled: bool = True
    api_key: str = ""


@dataclass
class GoogleScholarConfig:
    enabled: bool = False
    serpapi_key: str = ""


@dataclass
class DBLPConfig:
    enabled: bool = True


@dataclass
class CrossRefConfig:
    enabled: bool = True
    polite_pool: bool = True  # 使用 Polite Pool 需要邮箱
    mailto: str = ""


@dataclass
class COREConfig:
    enabled: bool = False
    api_key: str = ""


@dataclass
class SourcesConfig:
    arxiv: ArxivConfig = field(default_factory=ArxivConfig)
    semantic_scholar: SemanticScholarConfig = field(default_factory=SemanticScholarConfig)
    google_scholar: GoogleScholarConfig = field(default_factory=GoogleScholarConfig)
    dblp: DBLPConfig = field(default_factory=DBLPConfig)
    crossref: CrossRefConfig = field(default_factory=CrossRefConfig)
    core: COREConfig = field(default_factory=COREConfig)


@dataclass
class Dimension:
    name: str = ""
    description: str = ""


@dataclass
class SearchConfig:
    max_results_per_source: int = 30
    date_range_years: int = 3
    concurrent_requests: int = 5
    dedup_threshold: float = 0.85


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    dimensions: List[Dimension] = field(default_factory=list)
    search: SearchConfig = field(default_factory=SearchConfig)


def load_config(config_path: str) -> Config:
    """Load config from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    config = Config()
    if 'model' in data:
        config.model = ModelConfig(**data['model'])

    # 如果配置文件中 api_key 为空，根据 base_url 从对应环境变量读取
    if not config.model.api_key:
        if "nvidia" in config.model.base_url:
            config.model.api_key = os.getenv("NVIDIA_API_KEY", "")
        else:
            config.model.api_key = os.getenv("OPENROUTER_API_KEY", "")
    if 'sources' in data:
        sources = data['sources']
        config.sources = SourcesConfig(
            arxiv=ArxivConfig(**sources.get('arxiv', {})),
            semantic_scholar=SemanticScholarConfig(**sources.get('semantic_scholar', {})),
            google_scholar=GoogleScholarConfig(**sources.get('google_scholar', {})),
            dblp=DBLPConfig(**sources.get('dblp', {})),
            crossref=CrossRefConfig(**sources.get('crossref', {})),
            core=COREConfig(**sources.get('core', {}))
        )

        # 从环境变量读取 CORE API Key（如果配置中为空）
        if not config.sources.core.api_key:
            config.sources.core.api_key = os.getenv("CORE_API_KEY", "")

    if 'dimensions' in data:
        config.dimensions = [Dimension(**d) for d in data['dimensions']]
    if 'search' in data:
        config.search = SearchConfig(**data['search'])

    return config
