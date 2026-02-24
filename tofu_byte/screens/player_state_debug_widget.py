from textual.css.query import NoMatches
from textual.widgets import Static
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.containers import Vertical
from rich.text import Text  # New Import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tofu_byte.player.player import Player


class PlayerStateDebugWidget(Static):
    player_info = reactive(Text(), init=False)

    def compose(self) -> ComposeResult:
        with Vertical(classes="player-debug-container"):
            yield Static("Player State Debug", classes="player-debug-title")
            yield Static(self.player_info, id="player-state-info")

    def update_player_info(self, player: "Player") -> None:
        info_text = Text()
        info_text.append("Pos: ", style="bold green")
        info_text.append(f"{player.pos}\n")
        info_text.append("Vel: ", style="bold green")
        info_text.append(f"{player.velocity}\n")
        info_text.append("On Ground: ", style="bold green")
        info_text.append(f"{player.is_on_ground}\n")
        info_text.append("On Roof: ", style="bold green")
        info_text.append(f"{player.is_on_roof}\n")
        info_text.append("Anim State: ", style="bold green")
        info_text.append(f"{player.anim_state.__class__.__name__}\n")
        info_text.append("  Frame: ", style="bold yellow")
        info_text.append(
            f"{player.anim_state.frame}/{player.anim_state.max_frame - 1}\n"
        )
        info_text.append("  Dir: ", style="bold yellow")
        info_text.append(f"{player.anim_state.direction}\n")
        info_text.append("  Immortal: ", style="bold yellow")
        info_text.append(f"{player.anim_state.immortal}\n")
        info_text.append("  Cycles: ", style="bold yellow")
        info_text.append(f"{player.anim_state.animation_cycles_completed}\n")

        self.player_info = info_text

    def watch_player_info(self, player_info: Text) -> None:
        try:
            info_static_widget = self.query_one("#player-state-info", Static)
            info_static_widget.update(player_info)
        except NoMatches:
            pass
