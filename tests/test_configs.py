import textwrap
import pytest

from rex_utils.utils import load_config


@pytest.fixture
def default_config_file(tmp_path):
    path = tmp_path / "default.toml"
    path.write_text(
        textwrap.dedent(
            """
            [session.info]
            name = "Default Name"
            email = "default@example.com"

            [device.test_daq]
            gate_time = 1000
            averages = 100
            trace = false
            """
        )
    )
    return path


@pytest.fixture
def env_config_file(tmp_path):
    path = tmp_path / "env.toml"
    path.write_text(
        textwrap.dedent(
            """
            [session.info]
            name = "Env Name"

            [device.test_daq]
            trace = true

            [device.test_daq2]
            gate_time = 500
            averages = 10
            trace = true
            """
        )
    )
    return path


def test_load_config_default_only(default_config_file, monkeypatch):
    monkeypatch.delenv("REX_PROVIDED_OVERWRITE_PATH", raising=False)

    config = load_config(str(default_config_file))

    assert config["session"]["info"]["name"] == "Default Name"
    assert config["device"]["test_daq"]["trace"] is False


def test_load_config_env_only(env_config_file, monkeypatch):
    monkeypatch.setenv("REX_PROVIDED_OVERWRITE_PATH", str(env_config_file))

    config = load_config("non_existent_default.toml")

    assert config["session"]["info"]["name"] == "Env Name"
    assert config["device"]["test_daq"]["trace"] is True
    assert "test_daq2" in config["device"]


def test_load_config_merge_env_over_default(
    default_config_file, env_config_file, monkeypatch
):
    monkeypatch.setenv("REX_PROVIDED_OVERWRITE_PATH", str(env_config_file))

    config = load_config(str(default_config_file))

    # Env overrides default
    assert config["session"]["info"]["name"] == "Env Name"

    # Default preserved where env does not override
    assert config["session"]["info"]["email"] == "default@example.com"

    # Nested merge works
    assert config["device"]["test_daq"]["gate_time"] == 1000
    assert config["device"]["test_daq"]["trace"] is True

    # New device introduced by env
    assert "test_daq2" in config["device"]


def test_load_config_no_configs(monkeypatch):
    monkeypatch.delenv("REX_PROVIDED_OVERWRITE_PATH", raising=False)

    with pytest.raises(FileNotFoundError):
        load_config("does_not_exist.toml")
