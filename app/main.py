from fastapi import FastAPI


app = FastAPI(title="Driver Diary")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
