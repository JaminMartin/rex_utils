import time
from pathlib import Path

from example_daq import Test_daq

from rex_utils import Session


def test_fake_experiment():
    def a_measurement(config) -> None:
        # connect to a device, inherit its config & loop through its functions. ideally, all devices should have some "measure" like
        # function that handles sending the data over the socket.
        daq = Test_daq(config, connect_to_rex=True)
        daq2 = Test_daq(config, name="test_daq2", connect_to_rex=True)
        for i in range(3000):
            daq.measure()
            daq2.measure()

            time.sleep(5)

        return

    # This may soon be deprecated, instead passing in the config via rex exlusively.
    base_path = Path(__file__).parent

    config_path = base_path / "config.toml"
    print(config_path)

    session = Session(a_measurement, config_path)
    session.start()


if __name__ == "__main__":
    test_fake_experiment()
