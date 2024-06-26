"""REST-based node for Brooks Xpeel device"""

import datetime
import time
from pathlib import Path

from brooks_xpeel_driver import BROOKS_PEELER_DRIVER
from fastapi.datastructures import State
from wei.modules.rest_module import RESTModule
from wei.types.module_types import ModuleState, ModuleStatus
from wei.types.step_types import ActionRequest, StepResponse, StepStatus
from wei.utils import extract_version

rest_module = RESTModule(
    name="peeler_node",
    version=extract_version(Path(__file__).parent.parent / "pyproject.toml"),
    description="A node to control the Brooks Xpeel peeler device",
    model="Brooks Xpeel",
)
rest_module.arg_parser.add_argument(
    "--device",
    type=str,
    default="/dev/ttyUSB0",
    help="Serial device for communicating with the device",
)


@rest_module.startup()
def peeler(state: State):
    """Peeler startup handler."""
    state.peeler = None
    state.peeler = BROOKS_PEELER_DRIVER(state.device)
    print("Peeler online")


@rest_module.state_handler()
def state(state: State):
    """Returns the current state of the UR module"""
    if state.status not in [
        ModuleStatus.BUSY,
        ModuleStatus.ERROR,
        ModuleStatus.INIT,
        None,
    ] or (
        state.action_start
        and (datetime.datetime.now() - state.action_start > datetime.timedelta(0, 2))
    ):
        state.peeler.get_status()
        if state.peeler.status_msg == 3:
            state.status = ModuleStatus.ERROR
        elif state.peeler.status_msg == 0:
            state.status = ModuleStatus.IDLE

    return ModuleState(status=state.status, error="")


@rest_module.action(
    name="peel",
    description="Executes a peeling cycle on the Peeler device",
)
def peel(state: State, action: ActionRequest) -> StepResponse:
    """
    Peel a plate
    """
    print("peeling")
    state.peeler.seal_check()
    state.peeler.peel(1, 2.5)
    time.sleep(15)

    return StepResponse(
        action_msg="Peeling successful", action_response=StepStatus.SUCCEEDED
    )


if __name__ == "__main__":
    rest_module.start()
