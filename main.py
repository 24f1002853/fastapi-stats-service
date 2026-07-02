from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import time
import uuid
import jwt
from jwt import InvalidTokenError

app = FastAPI()

# -------------------------------
# Assignment 1 Configuration
# -------------------------------
ALLOWED_ORIGIN = "https://dash-o11rja.example.com"
EMAIL = "24f1002853@ds.study.iitm.ac.in"

# -------------------------------
# Assignment 2 Configuration
# -------------------------------
ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-wndcfjks.apps.exam.local"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

# -------------------------------
# Root Endpoint
# -------------------------------
@app.get("/")
async def home():
    return {"status": "running"}

# -------------------------------
# Middleware
# -------------------------------
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = str(time.time() - start)

    return response

# -------------------------------
# CORS Preflight
# -------------------------------
@app.options("/stats")
async def stats_options(request: Request):

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

    return Response(status_code=403)

# -------------------------------
# Statistics Endpoint
# -------------------------------
@app.get("/stats")
async def stats(request: Request, values: str):

    origin = request.headers.get("origin")

    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid input"}
        )

    if len(nums) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty input"}
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

    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return response

# -------------------------------
# JWT Verification Endpoint
# -------------------------------
@app.post("/verify")
async def verify(data: dict):

    token = data.get("token")

    if not token:
        return JSONResponse(
            status_code=401,
            content={"valid": False}
        )

    try:

        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={"valid": False}
        )
