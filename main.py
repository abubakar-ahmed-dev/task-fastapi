from fastapi import FastAPI

app = FastAPI(title="Task API", version="1.0")


@app.get("/", summary="Say hello")
def root():
    return {"message": "Hello, Task API"}
