from fastapi import FastAPI

app = FastAPI()

@app.get("/requests")
def get_requests():
    return 'Hello World'