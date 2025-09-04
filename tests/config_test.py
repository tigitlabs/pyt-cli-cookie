"""Tests for the cli module."""

import pytest  # noqa
from typer.testing import CliRunner
from template.config import ConfigModel, Config

runner = CliRunner()


@pytest.fixture()
def _logs_dir(tmp_path):
    d = tmp_path / "logs"
    d.mkdir(exist_ok=True)
    assert d.exists()
    return d


@pytest.fixture()
def _config_dir(tmp_path):
    d = tmp_path / "config"
    d.mkdir(exist_ok=True)
    assert d.exists()
    return d


@pytest.fixture()
def _config(monkeypatch, _config_dir, _logs_dir) -> Config:
    """Fixture for the Config class."""
    monkeypatch.setitem(ConfigModel.model_config, "env_prefix", "test_config_")
    monkeypatch.setenv("test_config_logs_dir", str(_logs_dir))

    class MockPlatformDirs:
        def __init__(self, appname, appauthor):
            self.appname = appname
            self.appauthor = appauthor

        @property
        def user_config_path(self):
            return _config_dir

    monkeypatch.setattr("template.config.PlatformDirs", MockPlatformDirs)
    config = Config()
    assert config.config_file == _config_dir / "config.yaml"
    assert config.config_file.exists() is False
    assert config.model.log_level == "INFO"
    assert config.model.logs_dir == _logs_dir
    return config


class TestConfigModel:
    """Tests for the ConfigModel."""

    def test_config_model_with_default_values(self):
        """Test the ConfigModel with default values."""
        config_model = ConfigModel()
        assert config_model.log_level == "INFO"

    def test_config_model_with_env_vars(self, monkeypatch, _logs_dir):
        """Test the ConfigModel with custom values."""
        monkeypatch.setitem(ConfigModel.model_config, "env_prefix", "test_config_")
        monkeypatch.setenv("test_config_logs_dir", str(_logs_dir))
        monkeypatch.setenv("test_config_log_level", "DEBUG")
        config_model = ConfigModel()
        assert config_model.log_level == "DEBUG"
        assert config_model.logs_dir == _logs_dir


class TestConfig:
    """Tests for the Config class."""

    def test_config_class_default_init(self, _config_dir, _logs_dir, monkeypatch) -> None:
        """Test init function."""
        monkeypatch.setitem(ConfigModel.model_config, "env_prefix", "test_config_")
        monkeypatch.setenv("test_config_logs_dir", str(_logs_dir))
        monkeypatch.setenv("test_config_log_level", "DEBUG")
        config = Config()
        config.config_file = _config_dir / "config.yaml"
        assert config.config_file.exists() is False
        assert config.model.log_level == "DEBUG"
        assert config.model.logs_dir == _logs_dir

    def test_config_class_init(self, _config_dir, _logs_dir, monkeypatch):
        """Test init with mocked PlatformDirs."""
        monkeypatch.setitem(ConfigModel.model_config, "env_prefix", "test_config_")
        monkeypatch.setenv("test_config_logs_dir", str(_logs_dir))

        class MockPlatformDirs:
            def __init__(self, appname, appauthor):
                self.appname = appname
                self.appauthor = appauthor

            @property
            def user_config_path(self):
                return _config_dir

        monkeypatch.setattr("template.config.PlatformDirs", MockPlatformDirs)
        config = Config()

        assert config.config_file == _config_dir / "config.yaml"
        assert config.config_file.exists() is False
        assert config.model.log_level == "INFO"
        assert config.model.logs_dir == _logs_dir

    def test_show_method(self, _config, capsys):
        """Test the show method."""
        _config.show()
        captured = capsys.readouterr()
        assert "Current configuration" in captured.out

    def test_save_file_method(self, _config, capsys):
        """Test the save file method."""
        _config._save_config()
        assert _config.config_file.exists() is True

    def test_init_method(self, _config):
        """Test the init method."""
        assert _config.config_file.exists() is False
        _config.init()
        assert _config.config_file.exists() is True
        assert isinstance(_config.model, ConfigModel)
