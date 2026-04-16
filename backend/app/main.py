# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.app.core.config import get_settings
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat_pipeline import ChatPipelineService
from backend.app.services.emotion_classifier import EmotionClassifierService
from backend.app.services.llm_inference import LLMInferenceService


def load_resources(app: FastAPI) -> None:
    settings = get_settings()
    tokenizer = AutoTokenizer.from_pretrained(settings.llm_model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(settings.llm_model_path, torch_dtype="auto")
    model.eval()

    emotion_service = EmotionClassifierService.from_model_name_or_path(settings.emotion_model_name_or_path)
    inference_service = LLMInferenceService(
        tokenizer=tokenizer,
        model=model,
        max_new_tokens=settings.max_new_tokens,
        temperature=settings.temperature,
        top_p=settings.top_p,
        repetition_penalty=settings.repetition_penalty,
    )
    app.state.chat_pipeline = ChatPipelineService(
        emotion_service=emotion_service,
        inference_service=inference_service,
        max_history_messages=settings.max_history_messages,
    )
    app.state.ready = True


def create_app(startup_loader=load_resources) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ready = False
        startup_loader(app)
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(request: Request) -> dict[str, str]:
        if not getattr(request.app.state, "ready", False):
            raise HTTPException(status_code=503, detail="models not ready")
        return {"status": "ready"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(payload: ChatRequest, request: Request):
        if not getattr(request.app.state, "ready", False):
            raise HTTPException(status_code=503, detail="models not ready")
        pipeline = request.app.state.chat_pipeline
        return pipeline.chat(payload.messages)

    return app


app = create_app()
