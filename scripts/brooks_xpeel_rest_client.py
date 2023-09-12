"""The server that takes incoming WEI flow requests from the experiment application"""
import json
from argparse import ArgumentParser
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from brooks_peeler_driver.brooks_peeler_driver.brooks_peeler_driver import BROOKS_PEELER_DRIVER
workcell = None
global peeler, state
serial_port = '/dev/ttyUSB0'
local_ip = 'parker.alcf.anl.gov'
local_port = 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    global peeler, state
    """Initial run function for the app, parses the worcell argument
        Parameters
        ----------
        app : FastApi
           The REST API app being initialized

        Returns
        -------
        None"""
    try:
            peeler = BROOKS_PEELER_DRIVER(serial_port)
            state = "IDLE"
    except Exception as err:
            print(err)
            state = "ERROR"

    # Yield control to the application
    yield

    # Do any cleanup here
    pass


app = FastAPI(lifespan=lifespan, )

@app.get("/state")
def get_state():
    global peeler, state
    if state != "BUSY":
        peeler.get_status()
        if peeler.status_msg == 3:
                    msg.data = 'State: ERROR'
                    state = "ERROR"

        elif peeler.status_msg == 0:
                    state = "IDLE"
    
                
    return JSONResponse(content={"State": state})#peeler.get_status() })

@app.get("/about")
async def about():
    global peeler, state
    return JSONResponse(content={"name": "peeler",
 "model": "Brooks_Xpeel",
 "version": "0.0.1",
 "actions": {
             "peel": "config : %s",  
             },
"repo": "https://github.com/AD-SDL/a4s_sealer_rest_node/edit/main/a4s_sealer_client.py"

 
 })
 #sealer.get_status() })

@app.get("/resources")
async def resources():
    global peeler, state
    return JSONResponse(content={"State": state })#peeler.get_status() })


@app.post("/action")
def do_action(
    action_handle: str,
    action_vars: str, 
):

    global peeler, state
    state = "BUSY"
    if action_handle == 'peel':  
        #self.peeler.set_time(3)
        #self.peeler.set_temp(175)]
      
        try: 
            print("peeling")
            peeler.seal_check
            peeler.peel(1, 2.5)
            time.sleep(15)  
            response_content = {
                    "action_msg": "StepStatus.Succeeded",
                    "action_response": "True",
                    "action_log": ""
                    
                    
                }
            state = "IDLE"
            return JSONResponse(content=response_content)
        except Exception as e:
            response_content = {
            "status": "failed",
            "error": str(e),
           
        }
            print(e)
            state = "IDLE"
            return JSONResponse(content=response_content)
   

if __name__ == "__main__":
    import uvicorn
    import a4s_peeler_client
    print(a4s_peeler_client)
    uvicorn.run("a4s_peeler_client.app", host=local_ip, port=local_port, reload=True)
