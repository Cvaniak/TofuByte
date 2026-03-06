from __future__ import annotations
from typing import Any
import httpx
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Button, Label, Static

from tofu_byte.mystatic import PrimaryScreenTitle
from tofu_byte.screens.const import COMMUNITY_MAPS, COMMUNITY_MAPS_DISCLAIMER
from tofu_byte.screens.screens import MenuScreenBase
from tofu_byte.tools import github_maps


class RepoWidget(Static):
    def __init__(self, repo: github_maps.Repo, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.repo = repo

    def compose(self) -> ComposeResult:
        with Container(classes="repo-info"):
            yield Label(f"Repo: {self.repo['name']}", classes="repo-name")
            yield Label(f"Owner: {self.repo['owner']['login']}", classes="repo-owner")
            yield Label(f"Stars: {self.repo['stargazers_count']}", classes="repo-stars")
            yield Label(f"URL: {self.repo['html_url']}", classes="repo-url")
        yield Button("Download", variant="success", classes="repo-download")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.notify(f"Downloading maps from {self.repo['name']}...")
        await github_maps.download_maps_from_repo(self.repo)
        self.notify(f"Maps from {self.repo['name']} downloaded.")


class GitHubMapsBrowser(MenuScreenBase[None]):
    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(COMMUNITY_MAPS)
        with Container(classes="body"):
            yield Static(COMMUNITY_MAPS_DISCLAIMER)
        with VerticalScroll(id="repos-list"):
            pass
        with Container():
            yield Button("Back", variant="error", id="back")

    async def on_mount(self) -> None:
        async with httpx.AsyncClient() as client:
            search_result = await github_maps.search_repositories(client)
            if search_result:
                repos_list = self.query_one("#repos-list", VerticalScroll)
                for repo in search_result["items"]:
                    repos_list.mount(RepoWidget(repo, classes="repo-widget"))
