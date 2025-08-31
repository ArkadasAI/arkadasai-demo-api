"""
ArkadasAI Demo API

This FastAPI application serves as a mock backend for ArkadasAI, providing
simple endpoints for authentication, plan retrieval, chat simulation, and
mock purchase confirmation. The API is designed to be deployed on a
managed hosting platform like Render or Railway and does not rely on
any local state outside of an in‑memory dictionary for demonstration
purposes.

Endpoints:
    - GET /health: Check service status.
    - POST /auth/register: Create a new user and return a token.
    - POST /auth/login: Log in an existing user and return a token.
    - GET /me: Retrieve current user information based on bearer token.
    - GET /plans: List available subscription plans.
    - POST /chat/send: Simulate a chat response with a small delay.
    - POST /purchase/confirm: Mock update of user subscription plan.

The application enables CORS for all origins so that mobile and web
clients can access the API without additional configuration.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
from typing import Dict, Optional


app = FastAPI(title="ArkadasAI Demo API", version="1.0.0")

# Allow any origin for demonstration; in production you may want to
# restrict this to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------
# Internal data storage
# ----------------------
# In‑memory storage for users and tokens. In a production application
# you would integrate with a database or authentication service.
USERS: Dict[str, Dict[str, str]] = {}
TOKENS: Dict[str, str] = {}

# List of available subscription plans
PLANS = [
    {"id": "free", "name": "Free", "desc": "Basic chat, limited usage", "price": "₺0"},
    {"id": "plus", "name": "Plus", "desc": "Faster replies, longer context", "price": "₺199/ay"},
    {"id": "pro", "name": "Pro", "desc": "Priority latency, enterprise features", "price": "₺499/ay"},
]


# ----------------------
# Pydantic models
# ----------------------
class RegisterIn(BaseModel):
    email: str
    password: str
    name: str = "Guest"


class LoginIn(BaseModel):
    email: str
    password: str


class ChatIn(BaseModel):
    message: str
    persona: Optional[str] = None


class PurchaseIn(BaseModel):
    plan: str  # expected values: "Plus" or "Pro"


# ----------------------
# Helper functions
# ----------------------
def mk_token(email: str) -> str:
    """Generate a unique token for a user and store it in TOKENS."""
    token = f"demo_{int(time.time() * 1000)}_{email.replace('@', '_')}"
    TOKENS[token] = email
    return token


def get_email_from_token(authorization: Optional[str]) -> str:
    """Retrieve the email associated with the provided Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    email = TOKENS.get(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    return email


# ----------------------
# Endpoint definitions
# ----------------------
@app.get("/health")
async def health() -> Dict[str, object]:
    """Return service health information."""
    return {"status": "ok", "service": "arkadasai-demo-api", "ts": int(time.time())}


@app.post("/auth/register")
async def register(data: RegisterIn) -> Dict[str, object]:
    """Register a new user. Returns token and user details."""
    if data.email in USERS:
        raise HTTPException(status_code=409, detail="User already exists")
    # In a real app you would hash the password and store it securely
    USERS[data.email] = {
        "id": f"user_{len(USERS) + 1}",
        "email": data.email,
        "name": data.name,
        "plan": "Free",
    }
    token = mk_token(data.email)
    return {"ok": True, "token": token, "user": USERS[data.email]}


@app.post("/auth/login")
async def login(data: LoginIn) -> Dict[str, object]:
    """Log in an existing user and return a token. Auto‑provision if not present."""
    # For demo we do not verify password. If email does not exist, create a user.
    if data.email not in USERS:
        USERS[data.email] = {
            "id": f"user_{len(USERS) + 1}",
            "email": data.email,
            "name": "Guest",
            "plan": "Free",
        }
    token = mk_token(data.email)
    return {"ok": True, "token": token, "user": USERS[data.email]}


@app.get("/me")
async def me(authorization: Optional[str] = Header(default=None, alias="Authorization")) -> Dict[str, object]:
    """Return the currently logged in user's info."""
    email = get_email_from_token(authorization)
    return {"ok": True, "user": USERS[email]}


@app.get("/plans")
async def get_plans() -> Dict[str, object]:
    """Return the list of available plans."""
    return {"ok": True, "plans": PLANS}


@app.post("/chat/send")
async def chat_send(
    payload: ChatIn,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, object]:
    """
    Simulate sending a chat message and return a dummy reply.

    Introduces a short delay to mimic real conversation latency.
    """
    email = get_email_from_token(authorization)
    persona = (payload.persona or "Arkadaş").lower()
    # Simulate network/processing delay
    await asyncio.sleep(1.5)
    reply_text = f"{persona.capitalize()} modu: Mesajını aldım — kısa demo yanıt."
    return {
        "ok": True,
        "sender": "assistant",
        "reply": reply_text,
        "user_plan": USERS[email]["plan"],
    }


@app.post("/purchase/confirm")
async def purchase_confirm(
    data: PurchaseIn,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, object]:
    """Mock confirmation of purchase, updating the user's subscription plan."""
    email = get_email_from_token(authorization)
    plan_lower = data.plan.strip().lower()
    if plan_lower not in {"plus", "pro"}:
        raise HTTPException(status_code=400, detail="plan must be Plus or Pro")
    USERS[email]["plan"] = "Plus" if plan_lower == "plus" else "Pro"
    return {"ok": True, "user": USERS[email]}