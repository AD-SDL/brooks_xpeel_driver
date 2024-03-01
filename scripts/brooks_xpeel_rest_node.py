"""The server that takes incoming WEI flow requests from the experiment application"""

from argparse import ArgumentParser
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from brooks_xpeel_driver.brooks_xpeel_driver import BROOKS_PEELER_DRIVER
from wei.core.data_classes import ModuleAbout, ModuleAction
from wei.helpers import extract_version
from pathlib import Path

global peeler, state
device = ""

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
    default="/dev/ttyUSB1",
    help="Serial device for communicating with the device",
)
args = parser.parse_args()
device = args.device


@asynccontextmanager
async def lifespan(app: FastAPI):
    global peeler, state, device
    """Initial run function for the app, parses the worcell argument
        Parameters
        ----------
        app : FastApi
           The REST API app being initialized

        Returns
        -------
        None"""
    try:
        peeler = BROOKS_PEELER_DRIVER(device)
        state = "IDLE"
    except Exception as err:
        print(err)
        state = "ERROR"

    # Yield control to the application
    yield

    # Do any cleanup here
    pass


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/state")
def get_state():
    global peeler, state
    if state != "BUSY":
        peeler.get_status()
        if peeler.status_msg == 3:
            state = "ERROR"
        elif peeler.status_msg == 0:
            state = "IDLE"

    return JSONResponse(content={"State": state})


@app.get("/about")
async def about():
    global peeler, state
    about = ModuleAbout(
        name="Brooks Xpeel",
        description="Brooks Xpeel is a  module that can peel covers off plates.",
        interface="wei_rest_node",
        version=extract_version(Path(__file__).parent.parent / "pyproject.toml"),
        actions=[
            ModuleAction(
                name="peel",
                description="This action peels a plate that is currenly in the peeling station.",
                args=[],
            )
        ],
        resource_pools=[],
    )
    return JSONResponse(content=about.model_dump(mode="json"))


@app.get("/resources")
async def resources():
    global peeler, state
    return JSONResponse(content={"State": state})


@app.post("/action")
def do_action(
    action_handle: str,
    action_vars: str,
):

    global peeler, state
    state = "BUSY"
    if action_handle == "peel":
        # self.peeler.set_time(3)
        # self.peeler.set_temp(175)]

        try:
            print("peeling")
            peeler.seal_check
            peeler.peel(1, 2.5)
            time.sleep(15)
            response_content = {
                "action_msg": "Peeling successful",
                "action_response": "succeeded",
                "action_log": "",
            }
            state = "IDLE"
            return JSONResponse(content=response_content)
        except Exception as e:
            response_content = {
                "action_response": "failed",
                "action_msg": "",
                "action_log": str(e),
            }
            print(e)
            state = "IDLE"
            return JSONResponse(content=response_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "brooks_xpeel_rest_node:app",
        host=args.host,
        port=args.port,
        reload=False,
    )
