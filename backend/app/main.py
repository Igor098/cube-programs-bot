from fastapi import FastAPI
from app.api.v1 import program_router, admin_programs_router, bot_program_router, bot_admin_router, admin_router

application = FastAPI()
application.include_router(program_router)
application.include_router(admin_router)
application.include_router(admin_programs_router)
application.include_router(bot_program_router)
application.include_router(bot_admin_router)


@application.get("/health")
async def health_check():
    return {"status": "ok"}
