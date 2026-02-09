from collections import defaultdict
import json
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

DEBUG: dict[str, str] = defaultdict(str)

GAME_VERSION = "0.1.0"

APP_NAME = "TofuByte"
APP_AUTHOR = "Cvaniak"

user_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
user_dir.mkdir(parents=True, exist_ok=True)


CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_FILE = CONFIG_DIR / "config.json"


# def find_project_root(start: Path | None = None) -> Path:
#     path = start or Path(__file__).resolve()
#     for parent in [path, *path.parents]:
#         if (parent / "pyproject.toml").exists():
#             return parent
#     raise RuntimeError("Project root not found")


PROJECT_DIR = Path(__file__).parent

RESOURCES_DIR = PROJECT_DIR / "resources"


# TODO: Not nice solution
should_check_input_system = True


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_setting(key, default=None):
    return load_config().get(key, default)


def set_setting(key, value) -> None:
    config = load_config()
    config[key] = value
    save_config(config)


def delete_setting(key) -> None:
    config = load_config()
    if key in config:
        del config[key]
        save_config(config)


def has_setting(key) -> bool:
    return key in load_config()


def update_config(updates: dict) -> None:
    config = load_config()
    config.update(updates)
    save_config(config)


def reset_config() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def load_from_config(obj, mapping: dict) -> None:
    config = load_config()
    for attr, key in mapping.items():
        if key in config:
            setattr(obj, attr, config[key])


def save_to_config(obj, mapping: dict) -> None:
    config = load_config()
    for attr, key in mapping.items():
        config[key] = getattr(obj, attr)
    save_config(config)
