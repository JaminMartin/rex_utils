import random as rd

import numpy as np

from rex_utils import Measurement, RexSupport


class Test_daq(RexSupport):
    __toml_config__ = {
        "device.test_daq": {
            "_section_description": "test_daq measurement configuration",
            "gate_time": {"_value": 0.1, "_description": "Time in seconds"},
            "averages": {"_value": 500, "_description": "Number of averages"},
            "trace": {
                "_value": False,
                "_description": "Sends mock time series data if set to True",
            },
        }
    }

    def __init__(self, config, name="test_daq", connect_to_rex=True):
        """
        A simulated device
        """
        self.state = 0
        self.connect_to_rex = connect_to_rex
        super().__init__(name=name)
        self.bind_config(config)
        self.logger.debug(f"{self.name} connected with this config {self.config}")

        if self.connect_to_rex:
            self.sock = self.tcp_connect()

        self.setup_config()

        self.measurements = {
            "counts": Measurement(data=[], unit="dimensionless"),
            "current (mA)": Measurement(data=[], unit="mA"),
            "trace (signal)": Measurement(data=[], unit="V"),
            "trace (time (s))": Measurement(data=[], unit="s"),
        }

        self.validate_measurements()

    def setup_config(self):
        self.gate_time = self.require_config("gate_time")
        self.averages = self.require_config("averages")
        self.trace_enabled = self.require_config("trace")

    def measure(self) -> float:
        data = 0
        for i in range(self.averages):
            data += rd.uniform(0.0, 2) * self.gate_time + self.state
        data /= self.averages

        self.measurements["counts"] = Measurement(
            data=[data],
            unit="dimensionless",
        )

        self.measurements["current (mA)"] = Measurement(
            data=[data * rd.uniform(0.0, 10.0)],
            unit="mA",
        )

        # Trace measurements
        if self.trace_enabled:
            time = np.linspace(0.0, 10.0, 20)
            noise = np.random.normal(0.0, 0.1, 20)
            trace_data = np.exp(-time) + noise

            self.measurements["trace (signal)"] = Measurement(
                data=trace_data.tolist(),
                unit="V",
            )

            self.measurements["trace (time (s))"] = Measurement(
                data=time.tolist(),
                unit="s",
            )

        self.state += 1

        if self.connect_to_rex:
            payload = self.create_payload()
            self.tcp_send(payload, self.sock)

        return self.measurements
