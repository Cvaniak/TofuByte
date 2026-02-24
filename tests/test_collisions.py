import pytest
from tofu_byte.game.scenarios import SCENARIOS, Scenario
from unittest.mock import MagicMock

from unittest.mock import patch, PropertyMock
from tofu_byte.game.game import ScenarioScene
from textual.message_pump import MessagePump
import asyncio


class HeadlessMediator:
    def mount_drawable(self, obj):
        pass

    def delete_drawable(self, obj):
        pass

    def update(self):
        pass

    def stats_clear(self, config):
        pass


class MockApp:
    def __init__(self):
        self.theme_variables = {
            "surface": "black",
            "surface-darken-3": "grey",
            "success": "green",
            "background": "black",
            "warning": "yellow",
            "accent": "red",
            "player-color": "blue",
            "warning-darken-3": "orange",
            "error": "red",
            "error-darker-3": "red",
            "error-lighten-3": "bright_red",
        }
        self.console = MagicMock()

    def post_message(self, msg):
        pass

    def bell(self):
        pass


def run_scenario_sync(scenario: Scenario):
    mock_app = MockApp()

    removed_types = []
    recorded_messages = []

    class TestMediator:
        def mount_drawable(self, obj):
            pass

        def update(self):
            pass

        def stats_clear(self, config):
            pass

        def delete_drawable(self, obj):
            removed_types.append(obj.type_name)

    def mock_post_message(self, message):
        recorded_messages.append(message.__class__.__name__)

    # Mock 'app' property and 'post_message'
    with (
        patch(
            "tofu_byte.objects.game_object.GameObject.app", new_callable=PropertyMock
        ) as mock_app_prop,
        patch.object(MessagePump, "post_message", mock_post_message),
    ):
        mock_app_prop.return_value = mock_app

        # 1. Instantiate ScenarioScene
        mediator = TestMediator()
        scene = ScenarioScene(mediator, scenario=scenario)
        scene.run = True  # Enable step execution in step()

        # 2. Simulation loop using unified step()
        loop = asyncio.new_event_loop()

        for _ in scenario.timeline:
            loop.run_until_complete(scene.step())

        loop.close()

    return scene.player, removed_types, recorded_messages, scene.objects


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_outcomes(scenario):
    player, removed_types, recorded_messages, objects = run_scenario_sync(scenario)

    assert player.pos == scenario.expected_pos, (
        f"Scenario '{scenario.name}' failed: expected pos {scenario.expected_pos}, got {player.pos}"
    )
    actual_state_name = player.anim_state.__class__.__name__
    assert actual_state_name == scenario.expected_state, (
        f"Scenario '{scenario.name}' failed: expected state {scenario.expected_state}, got {actual_state_name}"
    )

    for expected_removed in scenario.expected_removed_types:
        assert expected_removed in removed_types, (
            f"Scenario '{scenario.name}' failed: expected {expected_removed} to be removed"
        )

    for expected_msg in scenario.expected_messages:
        assert expected_msg in recorded_messages, (
            f"Scenario '{scenario.name}' failed: expected {expected_msg} message to be recorded"
        )

    for expected_obj in scenario.expected_object_positions:
        target_type = expected_obj["type"]
        target_pos = expected_obj["pos"]

        obj = next(
            (o for o in objects if o.type_name == target_type and o.pos == target_pos),
            None,
        )

        assert obj is not None, (
            f"Scenario '{scenario.name}' failed: expected {target_type} "
            f"at pos {target_pos}, but not found."
        )

    if scenario.expected_cycles > 0:
        assert player.anim_state.animation_cycles_completed >= scenario.expected_cycles
