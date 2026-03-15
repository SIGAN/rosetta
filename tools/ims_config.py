"""
Configuration management for IMS Publishing

Handles environment variables and configuration loading for RAGFlow-based
IMS publishing tools.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ims_utils import get_workspace_root
from typing_utils import JsonDict

def find_env_file(env_name: str | None = None) -> Path | None:
    """
    .env file discovery.
    
    Searches for .env files in this order:
    1. Current working directory with optional suffix (e.g., .env.remote)
    2. Script's directory (where ims_config.py is located) with optional suffix
    3. Workspace root (.git directory) with optional suffix
    4. Fallback: .env in any of the above locations
    
    This approach is folder-agnostic and works regardless of project structure.
    
    Args:
        env_name: Environment name (e.g., "remote", "dev"). If provided,
                  looks for .env.<env_name> first, then falls back to .env
    
    Returns:
        Path to .env file if found, None otherwise
        
    Examples:
        >>> find_env_file("remote")
        Path('/project/.env.remote')
        
        >>> find_env_file()
        Path('/project/.env')
    """
    search_paths = []
    
    # 1. Current working directory (where command is executed)
    search_paths.append(Path.cwd())
    
    # 2. Script's own directory (where this module lives)
    script_dir = Path(__file__).parent.absolute()
    if script_dir != Path.cwd():
        search_paths.append(script_dir)
    
    # 3. Workspace root (directory containing .git)
    workspace_root = Path.cwd()
    while workspace_root != workspace_root.parent:
        if (workspace_root / ".git").exists():
            if workspace_root not in search_paths:
                search_paths.append(workspace_root)
            break
        workspace_root = workspace_root.parent
    
    # Remove duplicates while preserving order
    search_paths = list(dict.fromkeys(search_paths))
    
    # Search for env file with intelligent fallback
    for search_dir in search_paths:
        if not search_dir.exists():
            continue
        
        # Try with environment suffix first (e.g., .env.remote)
        if env_name:
            env_file = search_dir / f".env.{env_name}"
            if env_file.exists():
                return env_file
        
        # Fall back to .env without suffix
        env_file = search_dir / ".env"
        if env_file.exists():
            return env_file
    
    return None


@dataclass
class IMSConfig:
    """
    RAGFlow configuration for IMS publishing.
    
    Environment Variables:
        RAGFLOW_BASE_URL: RAGFlow instance URL (e.g., http://ragflow.local)
        RAGFLOW_API_KEY: API key for authentication
        RAGFLOW_DATASET_DEFAULT: Default dataset name (default: "aia")
        RAGFLOW_DATASET_TEMPLATE: Template for dataset names (default: "aia-{release}")
        RAGFLOW_EMBEDDING_MODEL: Embedding model (format: model_name@provider)
        RAGFLOW_CHUNK_METHOD: Chunking method (default: "naive")
        RAGFLOW_CHUNK_TOKEN_NUM: Chunk size in tokens (default: 512)
        RAGFLOW_DELIMITER: Delimiter for splitting chunks (default: \n)
        RAGFLOW_AUTO_KEYWORDS: Auto-generate keywords per chunk (default: 0)
        RAGFLOW_AUTO_QUESTIONS: Auto-generate questions per chunk (default: 0)
        RAGFLOW_PAGE_SIZE: Page size for listing operations (default: 1000)
        RAGFLOW_PARSE_TIMEOUT: Timeout for parsing operations in seconds (default: 300)
        ENVIRONMENT: Environment name (default: "local")
    
    Examples:
        >>> config = IMSConfig.from_env(".env")
        >>> print(config.base_url)
        http://ragflow.local
        
        >>> config = IMSConfig.from_env_vars()
        >>> client = RAGFlowClient(config.api_key, config.base_url)
    """
    
    base_url: str
    api_key: str
    dataset_default: str = "aia"
    dataset_template: str = "aia-{release}"
    embedding_model: str | None = None
    chunk_method: str = "naive"
    parser_config: JsonDict | None = None
    environment: str = "local"
    page_size: int = 1000
    parse_timeout: int = 300
    
    @classmethod
    def from_env(
        cls,
        env_file: str | None = None,
        environment: str | None = None
    ) -> "IMSConfig":
        """
        Load configuration from .env file.
        
        Supports both explicit file paths and automatic discovery.
        
        Args:
            env_file: Explicit path to .env file. If not provided,
                     uses auto-discovery via find_env_file()
            environment: Environment name for auto-discovery (e.g., "remote").
                        Only used if env_file is not provided.
                        Looks for .env.<environment> or .env files.
            
        Returns:
            IMSConfig instance
            
        Raises:
            FileNotFoundError: If env file cannot be found or is not provided
            ValueError: If required environment variables are missing
            
        Examples:
            # Explicit file path
            >>> config = IMSConfig.from_env("ragflow.env")
            
            # Auto-discovery with environment
            >>> config = IMSConfig.from_env(environment="remote")
            # Searches for: .env.remote, then .env
            
            # Auto-discovery (looks for .env)
            >>> config = IMSConfig.from_env()
        """
        # Determine which file to load
        env_path: Path
        if env_file:
            # Explicit file path provided
            env_path = Path(env_file)
            if not env_path.exists():
                raise FileNotFoundError(f"Environment file not found: {env_file}")
        else:
            # Auto-discovery
            discovered_env_path = find_env_file(environment)
            if not discovered_env_path:
                env_hint = f" (tried .env.{environment} and .env)" if environment else " (tried .env)"
                raise FileNotFoundError(
                    f"No .env file found{env_hint}\n"
                    f"Current directory: {Path.cwd()}\n"
                    f"Workspace root: {get_workspace_root()}\n"
                    f"\nPlease create a .env file with RAGFLOW_BASE_URL and RAGFLOW_API_KEY"
                )
            env_path = discovered_env_path
        
        # Load environment variables from file
        load_dotenv(env_path)
        
        return cls.from_env_vars(environment=environment)
    
    @classmethod
    def from_env_vars(cls, environment: str | None = None) -> "IMSConfig":
        """
        Load configuration from environment variables.

        Args:
            environment: Optional explicit environment name (e.g., "local",
                "dev", "remote"). If provided, this value is used and takes
                precedence over the ENVIRONMENT environment variable. If not
                provided, the ENVIRONMENT variable is used, defaulting to
                "local" when unset.
        
        Returns:
            IMSConfig instance
            
        Raises:
            ValueError: If RAGFLOW_API_KEY is missing
            
        Examples:
            >>> os.environ["RAGFLOW_BASE_URL"] = "http://ragflow.local"
            >>> os.environ["RAGFLOW_API_KEY"] = "ragflow-xxx"
            >>> config = IMSConfig.from_env_vars()
        """
        base_url = os.getenv("RAGFLOW_BASE_URL", "http://ragflow.local")
        api_key = os.getenv("RAGFLOW_API_KEY", "")
        dataset_default = os.getenv("RAGFLOW_DATASET_DEFAULT", "aia")
        dataset_template = os.getenv("RAGFLOW_DATASET_TEMPLATE", "aia-{release}")
        # fallback to ENVIRONMENT env var, or default to "local"
        environment = environment or os.getenv("ENVIRONMENT", "local") or "local"
        
        # Dataset creation settings
        embedding_model = os.getenv("RAGFLOW_EMBEDDING_MODEL") or None
        chunk_method = os.getenv("RAGFLOW_CHUNK_METHOD", "naive")
        
        # Pagination and timeout settings
        page_size = int(os.getenv("RAGFLOW_PAGE_SIZE", "1000"))
        parse_timeout = int(os.getenv("RAGFLOW_PARSE_TIMEOUT", "300"))
        
        # Parser configuration for naive chunking
        parser_config: JsonDict | None = None
        if chunk_method == "naive":
            chunk_token_num = int(os.getenv("RAGFLOW_CHUNK_TOKEN_NUM", "512"))
            delimiter = os.getenv("RAGFLOW_DELIMITER", "\\n")
            auto_keywords = int(os.getenv("RAGFLOW_AUTO_KEYWORDS", "0"))
            auto_questions = int(os.getenv("RAGFLOW_AUTO_QUESTIONS", "0"))
            
            parser_config = {
                "chunk_token_num": chunk_token_num,
                "delimiter": delimiter.encode().decode('unicode_escape'),  # Handle \n escape
                "auto_keywords": auto_keywords,
                "auto_questions": auto_questions
            }
        
        return cls(
            base_url=base_url,
            api_key=api_key,
            dataset_default=dataset_default,
            dataset_template=dataset_template,
            embedding_model=embedding_model,
            chunk_method=chunk_method,
            parser_config=parser_config,
            environment=environment,
            page_size=page_size,
            parse_timeout=parse_timeout
        )
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.base_url:
            raise ValueError("base_url cannot be empty")
        
        if not self.api_key:
            raise ValueError("api_key cannot be empty")
        
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"base_url must start with http:// or https://, got: {self.base_url}"
            )
        
        if not self.api_key.startswith("ragflow-"):
            print(
                f"Warning: API key should start with 'ragflow-', got: {self.api_key[:10]}..."
            )
        
        return True
    
    def save_credentials(self, env_file: str = ".env") -> None:
        """
        Save credentials to .env file.
        
        Args:
            env_file: Path to .env file to create/update
            
        Examples:
            >>> config = IMSConfig(...)
            >>> config.save_credentials("ragflow.env")
        """
        env_path = Path(env_file)
        
        # Read existing content if file exists
        existing_lines: list[str] = []
        ragflow_keys = {
            "RAGFLOW_BASE_URL",
            "RAGFLOW_API_KEY",
            "RAGFLOW_DATASET_DEFAULT",
            "RAGFLOW_DATASET_TEMPLATE",
            "ENVIRONMENT"
        }
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    # Keep lines that don't set RAGFlow variables
                    if not any(line.startswith(f"{key}=") for key in ragflow_keys):
                        existing_lines.append(line.rstrip())
        
        # Build new content
        new_lines = existing_lines + [
            "",
            "# RAGFlow Configuration",
            f"RAGFLOW_BASE_URL={self.base_url}",
            f"RAGFLOW_API_KEY={self.api_key}",
            f"RAGFLOW_DATASET_DEFAULT={self.dataset_default}",
            f"RAGFLOW_DATASET_TEMPLATE={self.dataset_template}",
            f"ENVIRONMENT={self.environment}",
        ]
        
        # Write to file
        with open(env_path, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')
        
        print(f"Saved configuration to {env_file}")
    
    def __str__(self) -> str:
        """String representation (masks API key)"""
        masked_key = f"{self.api_key[:10]}..." if len(self.api_key) > 10 else "***"
        return (
            f"IMSConfig(\n"
            f"  base_url={self.base_url}\n"
            f"  api_key={masked_key}\n"
            f"  dataset_default={self.dataset_default}\n"
            f"  dataset_template={self.dataset_template}\n"
            f"  environment={self.environment}\n"
            f")"
        )
