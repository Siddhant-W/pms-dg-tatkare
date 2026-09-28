from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.auth.router import router as auth_router
from app.api.routes.teachers import router as teachers_router
from app.api.routes.timetable import router as timetable_router
from app.api.routes.attendance import router as attendance_router
from app.api.routes.proxy_requirements import router as proxy_req_router
from app.api.routes.proxy_assignments import router as proxy_assign_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.history import router as history_router

app = FastAPI(title="Presento Backend")

# A wildcard origin is invalid together with allow_credentials=True: the browser
# refuses to send/accept the HttpOnly refresh cookie. Origins must be explicit.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(teachers_router, prefix="/api")
app.include_router(timetable_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")
app.include_router(proxy_req_router, prefix="/api")
app.include_router(proxy_assign_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(history_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
