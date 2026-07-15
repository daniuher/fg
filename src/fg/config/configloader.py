import os
import tomllib
from pathlib import Path
from importlib.resources import files


def _default_config_path() -> Path:
    return files("fg.config").joinpath("default.toml")


def _xdg_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "fg" / "config.toml"


def _resolve_config_paths() -> list[Path]:
    paths = []
    env_override = os.environ.get("FG_CONFIG")
    if env_override:
        paths.append(Path(env_override).expanduser())

    local = Path.cwd() / "fg.toml"
    if local.exists():
        paths.append(local)

    user = _xdg_config_path()
    if user.exists():
        paths.append(user)

    return paths


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict:
    with open(_default_config_path(), "rb") as f:
        config = tomllib.load(f)

    for path in _resolve_config_paths():
        with open(path, "rb") as f:
            user_config = tomllib.load(f)
        config = _deep_merge(config, user_config)

    return config


CONFIG = load_config()
