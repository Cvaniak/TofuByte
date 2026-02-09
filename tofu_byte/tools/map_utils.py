import json
from pathlib import Path
from typing import Any

from tofu_byte.config import APP_AUTHOR, GAME_VERSION


def create_empty_map(file_name: Path, app_authors: list[str] = [APP_AUTHOR]):
    empty_map: dict[str, Any] = {
        "name": file_name.stem,
        "game_version": GAME_VERSION,
        "authors": app_authors,
        "objects": [{"type": "Player", "pos": [10, 10]}],
        "max_points": 1,
        "hp": 1,
    }
    with open(file_name, "w") as file:
        json.dump(empty_map, file)
