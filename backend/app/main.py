import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import firebase_admin
from firebase_admin import credentials as fb_credentials
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.services.neo4j_service import Neo4jService
from app.dependencies import set_neo4j_service
from app.routers import auth, contacts, search, network
from app.websocket.sync_handler import manager, handle_sync_message
from app.services.auth_service import verify_firebase_token

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Rate limiter (shared across the app)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Lifespan: startup + shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # --- Startup ---
    # Initialize Neo4j
    neo4j_service = Neo4jService(
        uri=settings.neo4j_uri,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
    try:
        neo4j_service.verify_connectivity()
        neo4j_service.create_indexes()
        logger.info("Neo4j connection established.")
    except Exception as exc:
        logger.warning("Neo4j not reachable at startup: %s", exc)

    set_neo4j_service(neo4j_service)

    # Initialize Firebase Admin SDK (only once)
    if not firebase_admin._apps:
        try:
            if settings.firebase_project_id:
                firebase_admin.initialize_app(
                    options={"projectId": settings.firebase_project_id}
                )
                logger.info("Firebase Admin SDK initialized (project: %s).", settings.firebase_project_id)
            else:
                firebase_admin.initialize_app()
                logger.info("Firebase Admin SDK initialized with default credentials.")
        except Exception as exc:
            logger.warning("Firebase Admin SDK initialization skipped: %s", exc)

    yield

    # --- Shutdown ---
    neo4j_service.close()
    logger.info("Neo4j connection closed.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ContactGraph API",
    version="1.0.0",
    description="REST + WebSocket backend for the ContactGraph Android app.",
    lifespan=lifespan,
)

# Rate-limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = (
    ["*"]
    if settings.allowed_origins.strip() == "*"
    else [o.strip() for o in settings.allowed_origins.split(",")]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(search.router)
app.include_router(network.router)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/v1/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/sync")
async def websocket_sync(
    websocket: WebSocket,
    token: str = Query(..., description="Firebase ID token for authentication"),
) -> None:
    """
    Real-time contact sync over WebSocket.

    Clients must pass their Firebase ID token as the ``token`` query parameter:
        ws://host/ws/sync?token=<firebase-id-token>
    """
    # Authenticate before accepting the connection
    try:
        decoded = verify_firebase_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    user_phone: str = decoded.get("phone_number", decoded.get("uid", "anonymous"))

    from app.dependencies import _neo4j_service  # noqa: PLC0415

    await manager.connect(websocket, user_phone)
    try:
        while True:
            raw = await websocket.receive_text()
            await handle_sync_message(websocket, user_phone, raw, _neo4j_service)
    except WebSocketDisconnect:
        manager.disconnect(user_phone)
