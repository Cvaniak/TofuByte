from dataclasses import dataclass
import json
from pathlib import Path

from textual.geometry import Offset

from tofu_byte.config import APP_AUTHOR, GAME_VERSION
from tofu_byte.objects.base_object import BaseObject
from tofu_byte.type_register import CLASS_REGISTRY


from tofu_byte.player.player import Player  # noqa: F401
from tofu_byte.objects.floor import Floor  # noqa: F401
from tofu_byte.objects.spikes import Spikes, SpikesDown  # noqa: F401
from tofu_byte.objects.light import Light  # noqa: F401
from tofu_byte.objects.stars import Star, EndBall  # noqa: F401
from tofu_byte.objects.floating_text import FloatingText  # noqa: F401

from typing import Any


@dataclass
class MapConfigObjects:
    objects: list[BaseObject | Player]


@dataclass
class MapConfigValues:
    hp: int = 1
    points: int = 1
    winning_ball: bool = False
    map_size: Offset = Offset(64, 64)


@dataclass
class MapMetadata:
    name: str
    game_version: str
    authors: list[str]


@dataclass
class MapData:
    objects: MapConfigObjects
    config: MapConfigValues
    metadata: MapMetadata


def load_json(file_name: Path) -> dict[Any, Any]:
    with open(file_name, "rb") as f:
        config = json.load(f)
    return config


def load_map(
    file: Path,
) -> MapData:
    map_config = load_json(file)
    objects = [
        CLASS_REGISTRY[obj["type"]].from_json(obj) for obj in map_config["objects"]
    ]
    config = MapConfigValues(
        hp=map_config["hp"],
        points=sum(obj["type"] == "Star" for obj in map_config["objects"]),
        winning_ball=any(obj["type"] == "EndBall" for obj in map_config["objects"]),
        map_size=Offset(64, 64),
    )
    metadata = MapMetadata(
        map_config.get("name", file.stem),
        map_config.get("game_version", GAME_VERSION),
        map_config.get("authors", [APP_AUTHOR]),
    )

    return MapData(
        MapConfigObjects(
            objects,
        ),
        config,
        metadata,
    )
