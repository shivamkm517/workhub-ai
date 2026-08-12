from fastapi import FastAPI


app = FastAPI(
    title="WorkHub API Gateway",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "service": "api-gateway",
        "status": "healthy",
    }