"""Tests the basic functionality of the Module."""

import time
import unittest
from pathlib import Path

import requests
from wei import ExperimentClient
from wei.types import Workcell


class TestWEI_Base(unittest.TestCase):
    """Base class for WEI's pytest tests"""

    def __init__(self, *args, **kwargs):
        """Basic setup for WEI's pytest tests"""
        super().__init__(*args, **kwargs)
        self.root_dir = Path(__file__).resolve().parent.parent
        self.workcell = Workcell.from_yaml(
            self.root_dir / Path("tests/workcell_defs/test_workcell.yaml")
        )
        self.server_host = self.workcell.config.server_host
        self.server_port = self.workcell.config.server_port
        self.url = f"http://{self.server_host}:{self.server_port}"
        self.module_url = "http://brooks_xpeel_module:2001"
        self.redis_host = self.workcell.config.redis_host
        self.experiment = ExperimentClient(
            server_host=self.server_host,
            server_port=self.server_port,
            experiment_name="Test_Experiment",
            working_dir=Path(__file__).resolve().parent,
        )
        # Check to see that server is up
        start_time = time.time()
        while True:
            try:
                if requests.get(self.url + "/up").status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(1)
            if time.time() - start_time > 60:
                raise TimeoutError("Server did not start in 60 seconds")


# class TestPeelerInterfaces(TestWEI_Base):
#     """Tests the basic functionality of the Brooks Xpeel Peeler Module."""

#     def test_module_about(self):
#         """Tests that the module's /about endpoint works"""
#         response = requests.get(self.module_url + "/about")
#         assert response.status_code == 200
#         ModuleAbout(**response.json())


if __name__ == "__main__":
    unittest.main()
