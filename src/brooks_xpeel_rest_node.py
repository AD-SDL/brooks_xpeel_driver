"""The server that takes incoming WEI flow requests from the experiment application"""

import time
import traceback
from argparse import ArgumentParser, Namespace
from contextlib import asynccontextmanager
from pathlib import Path

from brooks_xpeel_driver import BROOKS_PEELER_DRIVER
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from wei.core.data_classes import (
    ModuleAbout,
    ModuleAction,
    ModuleStatus,
    StepResponse,
    StepStatus,
)
from wei.helpers import extract_version

global peeler, state


def parse_args() -> Namespace:
    """Parses the command line arguments for the module"""
    parser = ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Hostname that the REST API will be accessible on",
    )
    parser.add_argument("--port", type=int, default=2001)
    parser.add_argument(
        "--device",
        type=str,
        default="/dev/ttyUSB0",
        help="Serial device for communicating with the device",
    )
    return parser.parse_args()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Starts the module REST server"""
    global peeler, state
    try:
        args = parse_args()
        peeler = BROOKS_PEELER_DRIVER(args.device)
        state = ModuleStatus.IDLE
    except Exception:
        traceback.print_exc()
        state = ModuleStatus.ERROR

    # Yield control to the application
    yield

    # Do any cleanup here
    pass


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/state")
def get_state():
    """Returns the current state of the instrument"""
    global peeler, state
    if state != ModuleStatus.BUSY:
        try:
            peeler.get_status()
            if peeler.status_msg == 3:
                state = ModuleStatus.ERROR
            elif peeler.status_msg == 0:
                state = ModuleStatus.IDLE
        except Exception:
            state = ModuleStatus.ERROR

    return JSONResponse(content={"State": state})


@app.get("/about")
async def about() -> ModuleAbout:
    """Returns information about the module's capabilities."""
    global peeler, state
    return ModuleAbout(
        name="Brooks Xpeel",
        description="Brooks Xpeel is a  module that can peel covers off plates.",
        interface="wei_rest_node",
        version=extract_version(Path(__file__).parent.parent / "pyproject.toml"),
        actions=[
            ModuleAction(
                name="peel",
                description="This action peels a plate that is currently in the peeling station.",
                args=[],
            )
        ],
        resource_pools=[],
    )


@app.get("/resources")
async def resources():
    """Returns information about any resource's managed by the module"""
    global peeler, state
    return JSONResponse(content={"State": state})


@app.post("/action")
def do_action(
    action_handle: str,
    action_vars: str,
) -> StepResponse:
    """Performs the action specified by 'action_handle'
    with arguments from 'action_vars' on the instrument."""
    global peeler, state
    if state != ModuleStatus.IDLE:
        return StepResponse(
            action_log=f"The instrument is not currently idle. State: {state}",
            action_response=StepStatus.FAILED,
        )
    state = ModuleStatus.BUSY
    if action_handle == "peel":
        try:
            print("peeling")
            peeler.seal_check()
            peeler.peel(1, 2.5)
            time.sleep(15)
            state = ModuleStatus.IDLE
            return StepResponse(
                action_msg="Peeling successful", action_response=StepStatus.SUCCEEDED
            )
        except Exception as e:
            traceback.print_exc()
            state = ModuleStatus.IDLE
            return StepResponse(
                action_msg="Peeling failed",
                action_response=StepStatus.FAILED,
                action_log=str(e),
            )


if __name__ == "__main__":
    import uvicorn

    args = parse_args()
    uvicorn.run(
        "brooks_xpeel_rest_node:app",
        host=args.host,
        port=args.port,
        reload=False,
    )
