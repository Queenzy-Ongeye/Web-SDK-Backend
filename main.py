import os
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from smile_id_core import WebApi

load_dotenv()

ALLOWED_PRODUCTS = {
    "authentication",
    "basic_kyc",
    "smartselfie",
    "biometric_kyc",
    "enhanced_kyc",
    "doc_verification",
    "enhanced_doc_verification",
}

app = FastAPI()

# For development, set your Vue dev server origin(s).
# In production, set your actual domain(s) and remove "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,  # set True only if you actually use cookies/auth
    allow_methods=["*"],
    allow_headers=["*"],
)



def require_env():
    partner_id = os.getenv("SMILE_PARTNER_ID")
    callback_url = os.getenv("CALLBACK_URL")
    api_key = os.getenv("SMILE_API_KEY")
    sid_server = os.getenv("SID_SERVER")

    missing = [k for k, v in {
        "SMILE_PARTNER_ID": partner_id,
        "CALLBACK_URL": callback_url,
        "SMILE_API_KEY": api_key,
        "SID_SERVER": sid_server,
    }.items() if not v]
    if missing:
        raise HTTPException(status_code=500, detail=f"Missing env vars: {', '.join(missing)}")

    # Inline SDK expects "sandbox" or "live"
    environment = "sandbox" if str(sid_server) == "0" else "live"

    return partner_id, callback_url, api_key, sid_server, environment


@app.get("/api/v1/token")
async def get_token(
    product: str = Query("biometric_kyc", description=f"One of: {', '.join(sorted(ALLOWED_PRODUCTS))}"),
    user_id: str | None = Query(None, description="Required for authentication. Must be an enrolled user_id."),
):
    if product not in ALLOWED_PRODUCTS:
        raise HTTPException(status_code=400, detail=f"Invalid product '{product}'. Allowed: {sorted(ALLOWED_PRODUCTS)}")

    partner_id, callback_url, api_key, sid_server, environment = require_env()

    # Authentication must reuse an already enrolled user_id (reference selfie exists)
    if product == "authentication":
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id is required for authentication and must refer to a previously enrolled user.",
            )
        final_user_id = user_id
    else:
        # Enrollment products: generate if not provided
        final_user_id = user_id or f"user-{uuid4()}"

    job_id = f"job-{uuid4()}"

    try:
        connection = WebApi(
            partner_id=partner_id,
            call_back_url=callback_url,
            api_key=api_key,
            sid_server=sid_server,
        )

        # Your SDK version uses (user_id, job_id, product)
        token_result = connection.get_web_token(final_user_id, job_id, product)
        token = token_result["token"] if isinstance(token_result, dict) and "token" in token_result else token_result

        return {
            "token": token,
            "partner_id": partner_id,
            "callback_url": callback_url,
            "environment": environment,
            "product": product,
            "user_id": final_user_id,
            "job_id": job_id,
        }

    except Exception as e:
        print(f"Error getting web token: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate token")


# Callback endpoint Smile can call (server-to-server)
@app.post("/smile/callback")
async def smile_callback(request: Request):
    payload = await request.json()
    # TODO: verify signatures if applicable + store payload
    print("Smile callback:", payload)
    return {"ok": True}

