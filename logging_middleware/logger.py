import httpx

def Log(stack,level,package,message):
    data = {
        "stack":stack,
        "level":level,
        "package":package,
        "message":message
    }
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJhbnVqYW1pcnRoYWxpbmdhbTFAZ21haWwuY29tIiwiZXhwIjoxNzc4MDU2NTAyLCJpYXQiOjE3NzgwNTU2MDIsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiI5MjFmNzYwZi0wZjM1LTQ5ZTktOWQyMC05MTk4YTJiYmEyOWIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJhbnVqIGEiLCJzdWIiOiI1OWQwMjExOC0wNTA1LTQzZTItYjRjZS1mMzUwZTk0MzY5ZmQifSwiZW1haWwiOiJhbnVqYW1pcnRoYWxpbmdhbTFAZ21haWwuY29tIiwibmFtZSI6ImFudWogYSIsInJvbGxObyI6ImNiLnNjLnU0Y3NlMjM1MDciLCJhY2Nlc3NDb2RlIjoiUFRCTW1RIiwiY2xpZW50SUQiOiI1OWQwMjExOC0wNTA1LTQzZTItYjRjZS1mMzUwZTk0MzY5ZmQiLCJjbGllbnRTZWNyZXQiOiJZaGh3eG15RHFqcXhoV1piIn0.akSk09TjyC3Gu-7p6EyXf5wrMUa8LDEwm1JXZYjWziE"
    }
    response = httpx.post("http://20.207.122.201/evaluation-service/logs", json=data, headers=headers)

    print(response.json())

Log("backend","info","service","testing the service")
