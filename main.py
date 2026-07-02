from fastapi import FastAPI, Request, Response,CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dash-o11rja.example.com"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

ALLOWED_ORIGIN = "https://dash-o11rja.example.com"
EMAIL = "24f1002853@ds.study.iitm.ac.in"


# -------- Middleware for headers --------
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response


# -------- CORS handling --------
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

    return Response(status_code=403)  # no ACAO header
@app.get("/")
async def home():
    return {"status": "running"}

# -------- Main endpoint --------
@app.get("/stats")
async def get_stats(request: Request, values: str):
    origin = request.headers.get("origin")

    # Parse values
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip()]
    except:
        return JSONResponse(status_code=400, content={"error": "Invalid input"})

    if not nums:
        return JSONResponse(status_code=400, content={"error": "Empty values"})

    count = len(nums)
    total = sum(nums)
    minimum = min(nums)
    maximum = max(nums)
    mean = total / count

    response = JSONResponse(
        content={
            "email": EMAIL,
            "count": count,
            "sum": total,
            "min": minimum,
            "max": maximum,
            "mean": mean,
        }
    )

    # Apply strict CORS
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return response
