"""Request-scoped provider injection; legacy Streamlit calls keep their SDK client."""
from contextvars import ContextVar

current = ContextVar("trace_runtime", default=None)


def client(*args, **kwargs):
    runtime = current.get()
    if runtime is not None and runtime.mode != "openai":
        return runtime.client
    from openai import OpenAI
    return OpenAI(*args, **kwargs)
