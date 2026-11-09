from fastapi import FastAPI

app = FastAPI(title="Job Extractor")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}