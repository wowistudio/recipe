import traceback
import uuid
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from recipe.core.settings import settings
from recipe.crud._base_public import NotFoundException


def get_error_info(exc: Exception) -> dict:
    # Additional diagnostic information
    exception_type = exc.__class__.__name__
    exception_str = str(exc)
    class_name = exception_str.split("\n")[0].split(" ")[-1]

    # Extract a simplified stack trace focusing on schema validation
    stack_trace = []
    if hasattr(exc, "__traceback__") and exc.__traceback__ is not None:
        stack_frames = traceback.extract_tb(exc.__traceback__)

        # Create a simplified version for the response
        for frame in stack_frames:
            # Only include frames from our backend code
            if ".venv" not in frame.filename:
                file = "/".join(frame.filename.split("/")[-3:])
                context = f"{file}::{frame.name}:{frame.lineno}"

                stack_trace.append(context)
    return {
        "class_name": class_name,
        "stack_trace": stack_trace,
        "type": exception_type,
    }


def unpack_validation_error(exc: ValidationError) -> dict[str, list[dict[str, str]]]:
    """Unpack a Pydantic validation error into a dictionary."""
    error_messages = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append({field: message})

    return {"errors": error_messages}

async def add_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to generate and add a request ID to the request for tracing.
    The request ID is added to the request state.
    """
    request.state.request_id = str(uuid.uuid4())
    return await call_next(request)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """Exception handler for validation errors

    Example of JSON output:
        {
            "errors": [
                {"body.email": "field required"},
                {"body.age": "value is not a valid integer"}
            ],
            "source": "RequestValidationError",
            "request_path": "/api/users",
            "request_method": "POST",
            "schema_info": {
                "name": "UserCreate",
                "module": "apps.schemas.user",
                "file_path": "/apps/schemas/user.py"
            },
            "validation_context": [
                "apps.api.v1.endpoints.users:create_user:42",
                "apps.schemas.user:UserCreate:15"
            ]
        }

    """
    # Extract basic error messages
    error_messages = unpack_validation_error(exc)  # type: ignore

    if settings.debug:
        return JSONResponse(
            status_code=422,
            content={
                **get_error_info(exc),
                "error_messages": error_messages,
            },
        )

    return JSONResponse(status_code=422, content=error_messages)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler for HTTPException.
    With debug mode, print useful information to the response for debugging purposes.
    """
    if settings.debug:
        info = get_error_info(exc)
        return JSONResponse(
            status_code= exc.status_code,
            content={
                "stack_trace": info["stack_trace"],
                "detail": exc.detail,
            },
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler for Exception.
    With debug mode, print useful information to the response for debugging purposes.
    """
    if settings.debug:
        info = get_error_info(exc)
        return JSONResponse(
            status_code=500,
            content={
                "stack_trace": info["stack_trace"],
                "detail": str(exc),
            },
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

async def not_found_exception_handler(
    request: Request, exc: NotFoundException
) -> JSONResponse:
    """Exception handler for NotFoundException.
    With debug mode, print useful information to the response for debugging purposes.
    """
    if settings.debug:
        info = get_error_info(exc)
        return JSONResponse(
            status_code=404,
            content={
                "stack_trace": info["stack_trace"],
                "detail": str(exc),
            },
        )
    return JSONResponse(status_code=404, content={"detail": str(exc)})