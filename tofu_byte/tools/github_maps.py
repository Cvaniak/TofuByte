import base64
import json
from pathlib import Path
import httpx
from typing import Any, Dict, List, Optional, TypedDict

from tofu_byte.config import GAME_VERSION, user_dir


class Owner(TypedDict):
    login: str


class Repo(TypedDict):
    name: str
    owner: Owner
    html_url: str
    stargazers_count: int


class SearchResult(TypedDict):
    items: List[Repo]


class Content(TypedDict):
    name: str
    path: str
    type: str
    content: str
    encoding: str


GITHUB_API_URL = "https://api.github.com"
TOPIC = "tofubyte-map"
HEADERS = {"Accept": "application/vnd.github.v3+json"}

user_maps_dir = user_dir / "maps"


async def search_repositories(
    client: httpx.AsyncClient,
) -> Optional[SearchResult]:
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {"q": f"topic:{TOPIC}"}
    try:
        response = await client.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error searching for repositories: {e}")
        return None


async def get_repo_contents(
    client: httpx.AsyncClient, repo: Repo
) -> Optional[List[Content]]:
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/contents"
    try:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting contents for repo {repo_name}: {e}")
        return None


async def get_file_content(
    client: httpx.AsyncClient, repo: Repo, path: str
) -> Optional[Content]:
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/contents/{path}"
    try:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting content for file {path} in repo {repo_name}: {e}")
        return None


def is_valid_map(content: Dict[str, Any]) -> bool:
    return (
        isinstance(content, dict)
        and "objects" in content
        and "name" in content
        and "authors" in content
        and "game_version" in content
        and isinstance(content["objects"], list)
        and isinstance(content["name"], str)
        and isinstance(content["authors"], list)
        and content["game_version"] < GAME_VERSION
    )


async def download_maps_from_repo(repo: Repo):
    repo_dir_name = f"{repo['owner']['login']}_{repo['name']}"
    repo_path = user_maps_dir / repo_dir_name
    repo_path.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient() as client:
        contents = await get_repo_contents(client, repo)
        if not contents:
            return

        for item in contents:
            if item["type"] == "file" and item["name"].endswith(".json"):
                file_content = await get_file_content(client, repo, item["path"])
                if file_content and "content" in file_content:
                    try:
                        content_data = base64.b64decode(file_content["content"]).decode(
                            "utf-8"
                        )
                        map_json = json.loads(content_data)
                        if is_valid_map(map_json):
                            map_name = item["name"]
                            map_path = repo_path / map_name
                            with open(map_path, "w") as f:
                                json.dump(map_json, f, indent=2)
                            print(f"  Downloaded valid map: {map_name} to {repo_path}")
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"  Error decoding or parsing {item['name']}: {e}")
