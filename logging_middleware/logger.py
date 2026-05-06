import httpx
from dotenv import load_dotenv
import os
load_dotenv()

def Log(stack,level,package,message):
    data = {
        "stack":stack,
        "level":level,
        "package":package,
        "message":message
    }
    token = os.getenv("AUTH_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = httpx.post("http://20.207.122.201/evaluation-service/logs", json=data, headers=headers)

    print(response.json())

Log("backend","info","service","testing the service")
