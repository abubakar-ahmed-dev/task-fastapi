from fastapi import FastAPI

app = FastAPI(title="Task API", version="1.0")


@app.get("/", summary="Show API information")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check server health")
def health():
    return {"status": "ok"}
