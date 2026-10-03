import asyncio
import json
import os
import platform
import shutil
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Header, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from . import engine
from .contracts import (
    RunInput,
    RunResult,
    DocumentsContext,
    URLsContext,
    Query,
    WorkflowEvent,
)
from .events import observer, install
from .storage import LocalStorage

storage = LocalStorage(os.environ.get("TRACE_DATA_DIR", "./.trace-data"))
slots = threading.BoundedSemaphore(2)
MAX_FILE = 200 * 1024 * 1024
install()


@asynccontextmanager
async def lifespan(app):
    async def cleanup():
        while True:
            await asyncio.sleep(60)
            await asyncio.to_thread(storage.cleanup)

    task = asyncio.create_task(cleanup())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="TRACE workflow adapter", version="1.0.0", lifespan=lifespan)
origins = os.environ.get("TRACE_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
if "*" in origins:
    raise RuntimeError("Configure exact frontend origins; wildcards are not allowed.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-OpenAI-Key"],
)


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        limit = (
            MAX_FILE + 1024 * 1024
            if scope.get("path", "").endswith("/uploads")
            else 1024 * 1024
        )
        size = 0

        async def bounded():
            nonlocal size
            message = await receive()
            size += len(message.get("body", b""))
            if size > limit:
                raise HTTPException(
                    413, "Request exceeds the permitted size (200 MB per file)."
                )
            return message

        headers = dict(scope.get("headers", []))
        if int(headers.get(b"content-length", b"0")) > limit:
            from fastapi.responses import JSONResponse

            return await JSONResponse(
                {"detail": "Request too large (200 MB per file)."}, status_code=413
            )(scope, receive, send)
        return await self.app(scope, bounded, send)


app.add_middleware(BodyLimit)


def session(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Create an anonymous session first.")
    return storage.session(authorization[7:])


def key(x_openai_key: str = Header(default="")):
    if len(x_openai_key) > 512:
        raise HTTPException(400, "Invalid API key.")
    return x_openai_key


def scrub(value, secret):
    if isinstance(value, str):
        return value.replace(secret, "[redacted]") if secret else value
    if isinstance(value, list):
        return [scrub(v, secret) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v, secret) for k, v in value.items()}
    return value


class Disconnected(BaseException):
    pass


def events(request, fn, secret):
    if not slots.acquire(blocking=False):
        raise HTTPException(
            429,
            "Two workflows are already running. Please retry explicitly when one completes.",
        )

    async def stream():
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        stopped = threading.Event()

        def send(event, data):
            if stopped.is_set():
                raise Disconnected()
            loop.call_soon_threadsafe(queue.put_nowait, (event, scrub(data, secret)))

        def work():
            token = observer.set(send)
            try:
                send("started", {"message": "Workflow started"})
                result = fn()
                send("result", result)
            except Disconnected:
                pass
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                message = (
                    "Invalid OpenAI credentials. Update your key in Settings."
                    if status == 401 and not isinstance(exc, HTTPException)
                    else str(exc.detail) if isinstance(exc, HTTPException) else str(exc)
                )
                try:
                    send(
                        "error",
                        {"message": message or "Workflow failed. Retry explicitly.", "code": "session_expired" if isinstance(exc, HTTPException) and status in {401,404} else "workflow_failed"},
                    )
                except Disconnected:
                    pass
            finally:
                observer.reset(token)
                slots.release()
                if not stopped.is_set():
                    loop.call_soon_threadsafe(queue.put_nowait, None)

        task = asyncio.create_task(asyncio.to_thread(work))
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                if event is None:
                    break
                name, data = event
                yield f"event: {name}\ndata: {json.dumps(data)}\n\n"
        finally:
            stopped.set()
            # A currently blocking provider call cannot be cancelled. Subsequent observed stages stop.
            await asyncio.shield(task)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/v1/health")
def health():
    from workflows.local_model import _model

    return {
        "ready": True,
        "architecture": platform.machine(),
        "local_model_loaded": _model is not None,
        "capabilities": {
            name: bool(shutil.which(cmd))
            for name, cmd in {
                "ocr": "tesseract",
                "javascript": "node",
                "java": "javac",
                "c": "gcc",
                "c++": "g++",
            }.items()
        },
        "retention_hours": 24,
        "max_concurrent_runs": 2,
    }


@app.post("/api/v1/sessions")
def create_session():
    return storage.create_session()


@app.delete("/api/v1/sessions/current", status_code=204)
def clear_session(sid=Depends(session)):
    storage.clear(sid)


@app.post("/api/v1/uploads")
async def upload(file: UploadFile = File(), sid=Depends(session)):
    name = Path(file.filename or "file").name
    if Path(name).suffix.lower() not in {
        ".pdf",
        ".docx",
        ".txt",
        ".png",
        ".jpg",
        ".jpeg",
    }:
        raise HTTPException(415, "Unsupported file type.")
    item, folder = storage.put(sid, "upload", name)
    size = 0
    try:
        with (folder / "file").open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE:
                    raise HTTPException(413, "Each file must be at most 200 MB.")
                handle.write(chunk)
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        with storage.connect() as db:
            db.execute("DELETE FROM items WHERE id=?", (item,))
        raise
    finally:
        await file.close()
    return {"file_id": item, "name": name, "size": size}


@app.post("/api/v1/runs", response_model=WorkflowEvent)
def run(inputs: RunInput, request: Request, sid=Depends(session), api_key=Depends(key)):
    return events(
        request, lambda: engine.execute(storage, sid, inputs, api_key), api_key
    )


@app.post("/api/v1/contexts/documents", response_model=WorkflowEvent)
def documents(
    inputs: DocumentsContext,
    request: Request,
    sid=Depends(session),
    api_key=Depends(key),
):
    if not api_key:
        raise HTTPException(400, "Enter an API key before processing documents.")
    return events(
        request,
        lambda: engine.context(storage, sid, "document-qa", inputs, api_key),
        api_key,
    )


@app.post("/api/v1/contexts/urls", response_model=WorkflowEvent)
def urls(
    inputs: URLsContext, request: Request, sid=Depends(session), api_key=Depends(key)
):
    if not api_key:
        raise HTTPException(400, "Enter an API key before processing URLs.")
    return events(
        request,
        lambda: engine.context(storage, sid, "url-qa", inputs, api_key),
        api_key,
    )


@app.post("/api/v1/contexts/{context_id}/query", response_model=WorkflowEvent)
def query(
    context_id: str,
    inputs: Query,
    request: Request,
    sid=Depends(session),
    api_key=Depends(key),
):
    if not api_key:
        raise HTTPException(400, "Enter an API key before asking a question.")
    return events(
        request,
        lambda: engine.query(storage, sid, context_id, inputs.question, api_key),
        api_key,
    )


@app.get("/api/v1/artifacts/{artifact_id}")
def artifact(artifact_id: str, sid=Depends(session)):
    row = storage.get(sid, artifact_id, "artifact")
    if not (row["folder"] / "file").is_file():
        raise HTTPException(
            404, "Artifact is no longer available. Run the workflow again explicitly."
        )
    return FileResponse(
        row["folder"] / "file",
        media_type=row["metadata"]["media_type"],
        headers={"Cache-Control": "private, no-store"},
    )


# Describe the actual SSE response while retaining the typed event schema.
from fastapi.openapi.utils import get_openapi


def openapi_schema():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    for path in [
        "/api/v1/runs",
        "/api/v1/contexts/documents",
        "/api/v1/contexts/urls",
        "/api/v1/contexts/{context_id}/query",
    ]:
        response = schema["paths"][path]["post"]["responses"]["200"]
        response["content"] = {
            "text/event-stream": {
                "schema": {"$ref": "#/components/schemas/WorkflowEvent"}
            }
        }
        response["description"] = (
            "Request-bound events: started, stage, warning, result, error. These are workflow observations, not model tokens."
        )
    app.openapi_schema = schema
    return schema


app.openapi = openapi_schema
