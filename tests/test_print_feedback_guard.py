"""Offline tests for the portable Print Bitch interaction guards."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

PLUGIN_PATH = Path(__file__).parents[1] / "plugins/print-feedback/__init__.py"
spec = importlib.util.spec_from_file_location("print_feedback", PLUGIN_PATH)
assert spec is not None and spec.loader is not None
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


class GuardTests(unittest.TestCase):
    def setUp(self):
        plugin.reset_state()

    def invoke(self, command="status", *, profile="3dprinting", session="s", turn="t"):
        return plugin.guard_repeated_terminal(
            tool_name="terminal", args={"command": command}, profile=profile,
            session_id=session, turn_id=turn)

    def test_third_duplicate_command_is_blocked_per_turn(self):
        self.assertIsNone(self.invoke())
        self.assertIsNone(self.invoke())
        self.assertEqual("block", self.invoke()["action"])

    def test_distinct_commands_and_new_turn_are_not_blocked(self):
        for i in range(50):
            self.assertIsNone(self.invoke(f"command-{i}"))
        self.assertIsNone(self.invoke(session="s", turn="next"))

    def test_other_profile_and_missing_identity_are_ignored(self):
        self.assertIsNone(self.invoke(profile="default"))
        self.assertIsNone(self.invoke(turn=""))

    def test_clarify_choices_are_capped_without_losing_other_path(self):
        args = {"questions": [{"question": "Pick", "choices": list("abcdef")}],
                "other": "preserved"}
        result = plugin.cap_clarifications(
            tool_name="clarify", args=args, platform="discord", profile="3dprinting")
        self.assertEqual("modify", result["action"])
        self.assertEqual(list("abcd"), result["args"]["questions"][0]["choices"])
        self.assertIn("Other", result["args"]["questions"][0]["question"])
        self.assertEqual("preserved", result["args"]["other"])

    def test_small_choice_list_and_non_discord_are_unchanged(self):
        args = {"questions": [{"question": "Pick", "choices": ["yes", "no"]}]}
        self.assertIsNone(plugin.cap_clarifications(
            tool_name="clarify", args=args, platform="discord", profile="3dprinting"))
        with mock.patch.dict("os.environ", {"PRINT_BITCH_PROFILE": "printer"}):
            self.assertIsNone(plugin.cap_clarifications(
                tool_name="clarify", args=args, platform="discord", profile="3dprinting"))
        self.assertIsNone(plugin.cap_clarifications(
            tool_name="clarify", args=args, platform="matrix", profile="3dprinting"))

    def test_registers_only_non_operational_hooks(self):
        ctx = mock.Mock()
        plugin.register(ctx)
        self.assertEqual(
            [("pre_tool_call", plugin.cap_clarifications),
             ("pre_tool_call", plugin.guard_repeated_terminal)],
            [call.args for call in ctx.register_hook.call_args_list])


if __name__ == "__main__":
    unittest.main()
