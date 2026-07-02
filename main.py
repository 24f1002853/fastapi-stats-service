from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-o11rja.example.com"
EMAIL = "24f1002853@ds.study.iitm.ac.in"


# Root endpoint (optional but recommended)
@app.get("/")
async def home():
    return {"status": "running"}


# Middleware for request headers
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response


# OPTIONS endpoint for CORS preflight
@app.options("/stats")
async def preflight(request: Request):
    origin = request.headers.get("origin")

    if origin == ALLOWED_ORIGIN:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
        )

    # Reject other origins without ACAO header
    return Response(status_code=403)


# GET endpoint
@app.get("/stats")
async def get_stats(request: Request, values: str):
    origin = request.headers.get("origin")

    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid input"}
        )

    if not nums:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty values"}
        )

    response = JSONResponse(
        content={
            "email": EMAIL,
            "count": len(nums),
            "sum": sum(nums),
            "min": min(nums),
            "max": max(nums),
            "mean": sum(nums) / len(nums),
        }
    )

    # Only the allowed origin gets ACAO
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return response
