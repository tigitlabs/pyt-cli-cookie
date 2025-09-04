"""Config Provider.

Handles reading and writing configuration files.
"""

from pathlib import Path

import pydantic_yaml
import typer
from loguru import logger
from platformdirs import PlatformDirs
from pydantic_settings import BaseSettings, SettingsConfigDict

config_app = typer.Typer(name="config", no_args_is_help=True, help="Configuration related commands.")
APP_NAME = "template"
APP_AUTHOR = "template"


class ConfigModel(BaseSettings):
    """Application configuration model.

    BaseSettings uses the defaults if no values are provided, or no environment variables are set.
    """

    model_config = SettingsConfigDict(env_prefix=f"{APP_NAME}_", env_ignore_empty=True, env_file=".env")
    logs_dir: Path = PlatformDirs(APP_NAME, APP_AUTHOR).user_log_path
    log_level: str = "INFO"


class Config:
    """Represents the Template application configuration."""

    model: ConfigModel

    def __init__(self) -> None:
        """Initialize the Config class."""
        self.config_file = PlatformDirs(APP_NAME, APP_AUTHOR).user_config_path / "config.yaml"
        self.model = ConfigModel()

    def init(self) -> None:
        """Initialize the configuration."""
        if self.config_file.exists() is False:
            self.model = ConfigModel()
            self._save_config()
        self.model = self._load_config()

    def show(self) -> None:
        """Show the current configuration."""
        print("Current configuration:")
        print(f"Config file: {self.config_file}")
        print(pydantic_yaml.to_yaml_str(self.model))

    def _load_config(self) -> ConfigModel:
        """Load the config from the file."""
        logger.debug(f"Loading configuration from {self.config_file}")
        return pydantic_yaml.parse_yaml_file_as(ConfigModel, self.config_file)

    def _save_config(self) -> None:
        """Save the config to the file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(pydantic_yaml.to_yaml_str(self.model))
        logger.debug(f"Config saved to: {self.config_file}")


config = Config()
config.init()


@config_app.callback()
def config_callback():
    """Callback for config commands."""
    print("Initializing configuration")
    config.init()


@config_app.command()
def show():
    """Show the current configuration."""
    config.show()
