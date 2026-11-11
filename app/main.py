import logging
from functools import lru_cache

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.extractor import extract_job
from app.providers.base import LLMProvider, LLMProviderError
from app.providers.gemini import GeminiProvider
from app.schemas import ExtractRequest, JobPosting

logger = logging.getLogger(__name__)

app = FastAPI(title="Job Extractor")


@lru_cache
def get_provider() -> LLMProvider:
    return GeminiProvider.from_env()


@app.exception_handler(LLMProviderError)
async def handle_provider_error(request: Request, exc: LLMProviderError) -> JSONResponse:
    logger.error("AI provider error: %s", exc)
    return JSONResponse(
        status_code=502,
        content={"detail": "The AI service could not process the request. Please try again in a moment."},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract-job", response_model=JobPosting)
def extract_job_endpoint(
    body: ExtractRequest, provider: LLMProvider = Depends(get_provider)
) -> JobPosting:
    return extract_job(body.text, provider)