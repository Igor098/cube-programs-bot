import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from api.v1 import program_router, admin_programs_router, bot_program_router, bot_admin_router, admin_router

application = FastAPI()
application.include_router(program_router)
application.include_router(admin_router)
application.include_router(admin_programs_router)
application.include_router(bot_program_router)
application.include_router(bot_admin_router)



# 1) 422 при ошибке парсинга запроса (body/query/path)
@application.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    print(">> Caught RequestValidationError", exc.errors())  # увидишь в консоли
    return JSONResponse(
        status_code=422,
        content={"status": "error", "where": "request", "errors": exc.errors(), "body": exc.body},
    )

# 2) 500 при ошибке валидации ОТВЕТА (модель response_model не совпала)
@application.exception_handler(ResponseValidationError)
async def response_validation_handler(request: Request, exc: ResponseValidationError):
    print(">> Caught ResponseValidationError", exc.errors())
    return JSONResponse(
        status_code=500,
        content={"status": "error", "where": "response", "errors": exc.errors()},
    )


@application.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=43445)
