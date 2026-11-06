# Tests

Use Python 3.14 for Home Assistant 2026.10.1, or Python 3.13 for the integration's
minimum supported Home Assistant 2025.2.0:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

For the minimum-version run, substitute `python3.13` and a separate virtualenv.
The dependency markers select the matching HA version.

The tests use real Home Assistant config-entry setup/retry and coordinator
behavior. Synthetic provider results and the platform-manager/loader boundaries
are mocked; actual network/node sensor objects verify populated data and stable
unique IDs. No Eero account, credentials, network access or live HA is used.

Cases cover provider failure, timeout, missing/empty initial data, native startup
retry, no duplicate platforms/listeners, unchanged entry data/options, first-call
success, acceptance of a nonempty cached account and an intentionally empty
selection. The API's own provider-exception logging is outside these setup tests.

## Vanished clients and Thread attributes

`test_vanished_client.py` builds real account objects for one update that lists a client and one that no longer does, then computes the client's switch and binary sensor states through Home Assistant's own state calculation. The entities go unavailable, keep their names and hang off the current update; upstream 1.8.1 raises `AttributeError: 'EeroNetwork' object has no attribute 'paused'`.

`test_thread_attributes.py` checks that the Thread switch publishes no Thread network key, commissioning credential or active operational dataset.
