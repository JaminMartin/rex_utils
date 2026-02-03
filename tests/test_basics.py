import time
import pytest

from rex_utils import Measurement, RexSupport


class YourClass(RexSupport):
    def __init__(self, config):
        self.config = config
        self.init_time_s = time.time()
        self.measurements = {}


# -----------------------
# Fixtures
# -----------------------


@pytest.fixture
def obj():
    instance = YourClass(config={})
    instance.config = {
        "level1": {"level2": {"target_key": "expected_value"}},
        "other_key": "other_value",
    }
    instance.init_time_s = time.time() - 100
    instance.name = "test_device"

    instance.measurements = {
        "temperature (C)": Measurement(data=[22.5, 23.0], unit="C"),
        "pressure (kPa)": Measurement(data=[101.2], unit="kPa"),
    }

    return instance


# -----------------------
# Config lookup tests
# -----------------------


def test_find_key_existing(obj):
    assert obj.find_key("target_key", obj.config) == "expected_value"


def test_find_key_missing(obj):
    with pytest.raises(ValueError):
        obj.find_key("non_existent_key", obj.config)


def test_require_config_success(obj):
    assert obj.require_config("target_key") == "expected_value"


def test_require_config_failure(obj):
    with pytest.raises(ValueError):
        obj.require_config("missing_key")


# -----------------------
# Payload creation tests
# -----------------------


def test_create_payload_structure(obj):
    payload = obj.create_payload()

    assert payload["device_name"] == "test_device"
    assert "device_config" in payload
    assert "measurements" in payload

    measurements = payload["measurements"]

    assert measurements["temperature (C)"]["unit"] == "C"
    assert measurements["temperature (C)"]["data"] == [22.5, 23.0]

    assert measurements["pressure (kPa)"]["unit"] == "kPa"
    assert measurements["pressure (kPa)"]["data"] == [101.2]
