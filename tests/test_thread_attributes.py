"""The Thread switch publishes no Thread credentials as state attributes."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.eero.switch import SWITCH_DESCRIPTIONS

SECRETS = {
    "thread_network_key",
    "commissioning_credential",
    "active_operational_dataset",
}


class ThreadAttributeTests(unittest.TestCase):
    def test_thread_switch_omits_credentials(self):
        thread = next(d for d in SWITCH_DESCRIPTIONS if d.key == "thread_enabled")
        self.assertFalse(SECRETS & set(thread.extra_attrs))
        self.assertIn("thread_network_name", thread.extra_attrs)


if __name__ == "__main__":
    unittest.main()
