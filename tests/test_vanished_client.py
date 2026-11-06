"""Regression tests for entities of a client that leaves the API response."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.eero.api.account import EeroAccount
from custom_components.eero.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
    EeroBinarySensorEntity,
)
from custom_components.eero.const import (
    CONF_PREFIX_NETWORK_NAME,
    CONF_SUFFIX_CONNECTION_TYPE,
)
from custom_components.eero.switch import SWITCH_DESCRIPTIONS, EeroSwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

NETWORK_URL = "/2.2/networks/1"
CLIENT_ID = "phone"


def account(*, with_client: bool) -> EeroAccount:
    """Return an account as one update builds it, listing the client or not."""
    client = {
        "url": f"{NETWORK_URL}/devices/{CLIENT_ID}",
        "nickname": "Phone",
        "mac": "02:00:00:00:00:01",
        "connected": True,
        "paused": False,
        "wireless": False,
    }
    network = {
        "url": NETWORK_URL,
        "name": "Home",
        "devices": {"data": [client] if with_client else []},
        "eeros": {"data": []},
        "profiles": {"data": []},
    }
    return EeroAccount(None, {"networks": {"data": [network]}})


def description(descriptions, key):
    """Return the entity description with KEY."""
    return next(d for d in descriptions if d.key == key)


class VanishedClientTests(unittest.IsolatedAsyncioTestCase):
    """A client eero stops listing makes its entities unavailable, not raise."""

    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.hass = HomeAssistant(self.directory.name)
        self.coordinator = SimpleNamespace(
            data=account(with_client=True), last_update_success=True
        )
        miscellaneous = {
            CONF_PREFIX_NETWORK_NAME: True,
            CONF_SUFFIX_CONNECTION_TYPE: False,
        }
        self.entities = {
            "paused": EeroSwitchEntity(
                self.coordinator,
                "1",
                CLIENT_ID,
                description(SWITCH_DESCRIPTIONS, "paused"),
                miscellaneous,
            ),
            "connected": EeroBinarySensorEntity(
                self.coordinator,
                "1",
                CLIENT_ID,
                description(BINARY_SENSOR_DESCRIPTIONS, "connected"),
                miscellaneous,
            ),
        }
        for key, entity in self.entities.items():
            entity.hass = self.hass
            entity.entity_id = f"test.{key}"

    async def asyncTearDown(self):
        await self.hass.async_stop(force=True)

    def states(self):
        """Compute each entity's state as Home Assistant does on a state write."""
        return {
            key: entity._async_calculate_state()
            for key, entity in self.entities.items()
        }

    async def test_client_listed(self):
        states = self.states()
        self.assertEqual(states["paused"].state, STATE_OFF)
        self.assertEqual(states["connected"].state, STATE_ON)

    async def test_client_leaves_then_returns(self):
        names = {key: entity.name for key, entity in self.entities.items()}

        self.coordinator.data = account(with_client=False)
        states = self.states()
        for key, entity in self.entities.items():
            self.assertFalse(entity.available, key)
            self.assertEqual(states[key].state, STATE_UNAVAILABLE, key)
            # Name and attributes still resolve from the last known copy.
            self.assertEqual(entity.name, names[key], key)
            # The kept copy hangs off the current update, not the one it came from.
            self.assertIs(
                entity.resource.network,
                self.coordinator.data.resource_index["1"][0],
                key,
            )

        self.coordinator.data = account(with_client=True)
        states = self.states()
        self.assertTrue(all(entity.available for entity in self.entities.values()))
        self.assertEqual(states["paused"].state, STATE_OFF)
        self.assertEqual(states["connected"].state, STATE_ON)


if __name__ == "__main__":
    unittest.main()
