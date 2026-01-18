"""
⚡ MistralMeter - LLM Evaluation Platform

A production-ready API for evaluating Mistral LLM performance.
Measures latency, token usage, and response quality with statistical rigor.

Design Principles:
- Model-agnostic evaluation (evaluated model ≠ judge model)
- Metrics independent from LLM provider
- Variance capture for reliable benchmarking
- Human-in-the-loop support for calibration

Author: Malek Gatoufi
Repository: github.com/malekgatoufi/mistralmeter
"""

import os
import json
from pathlib import Path
from typing import Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.schemas import (
    EvalPrompt,
    EvalRequest,
    BatchEvalRequest,
    CompareRequest,
    EvalResult,
    EvalResultWithVariance,
    BatchEvalResult,
    CompareResult,
    EvalDataset,
    DatasetInfo,
    MistralModel,
    ExpectedStyle,
    HumanRating
)
from app.runner import MistralRunner
from app.evaluator import LLMEvaluator
from app.metrics import aggregate_metrics, compare_metrics, compute_variance_metrics

# Load environment variables
load_dotenv()

# ============ Security Configuration ============

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# API Key security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Load allowed API keys from environment
ALLOWED_API_KEYS = set(
    key.strip() 
    for key in os.getenv("API_KEYS", "").split(",") 
    if key.strip()
)

# Enable/disable authentication
AUTH_ENABLED = os.getenv("ENABLE_AUTH", "false").lower() == "true"


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify API key if authentication is enabled."""
    if not AUTH_ENABLED:
        return True
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'X-API-Key' header."
        )
    
    if api_key not in ALLOWED_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return True


# Global instances (initialized on startup)
runner: Optional[MistralRunner] = None
evaluator: Optional[LLMEvaluator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    global runner, evaluator
    
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key:
        runner = MistralRunner(api_key=api_key)
        evaluator = LLMEvaluator(api_key=api_key)
        print("⚡ MistralMeter initialized successfully")
    else:
        print("⚠️ MISTRAL_API_KEY not set - API will not work")
    
    yield
    
    print("👋 MistralMeter shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="⚡ MistralMeter API",
    description="""
## Production-Grade LLM Evaluation Platform

**MistralMeter** provides comprehensive metrics, statistical analysis, and human-in-the-loop calibration for Mistral AI models.

### 🔒 Security Features
- **Rate Limiting**: 10 requests/minute per IP for evaluation endpoints
- **API Key Authentication**: Optional authentication (set ENABLE_AUTH=true)
- **CORS Protection**: Configurable origins
- **Cost Monitoring**: Track token usage and estimated costs

### 🎯 Core Features
- **Single Prompt Evaluation**: Test individual prompts with detailed metrics
- **Multi-Run Variance Analysis**: Capture LLM stochasticity with statistical analysis
- **Batch Evaluation**: Evaluate multiple prompts with aggregated statistics  
- **Model Comparison**: Side-by-side comparison of different models
- **LLM-as-Judge**: Automated quality scoring using AI evaluation (judge ≠ evaluated model)
- **Human-in-the-Loop**: Optional human ratings for judge calibration
- **Streaming**: Real-time response streaming

### 📊 Metrics Collected
| Metric | Description |
|--------|-------------|
| ⏱️ Latency | Total response time, TTFT, p50/p95 |
| 🔢 Tokens | Input/output counts, tokens/sec |
| 🧠 Quality | AI-evaluated score (0-10) with criteria breakdown |
| 📈 Variance | Std dev, mean, percentiles across runs |

### 🔬 Design Principles
1. **Judge ≠ Model** - Evaluated model is never the judge (reduces bias)
2. **Variance Aware** - Multiple runs for statistical confidence
3. **Provider Agnostic** - Metrics independent from LLM provider
4. **Human Calibration** - LLM scores validated by human ratings

### 🚀 Quick Start
```python
import requests

response = requests.post("http://localhost:8000/evaluate", json={
    "prompt": {"prompt": "Explain transformers"},
    "model": "mistral-small-latest",
    "judge_model": "mistral-large-latest",
    "runs": 3
})
```

---
*Built by Malek Gatoufi for the Mistral AI internship application.*
    """,
    version="2.0.0",
    lifespan=lifespan,
    contact={
        "name": "Malek Gatoufi",
        "email": "malek.gatoufi@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {"name": "Health", "description": "Service health and status"},
        {"name": "Evaluation", "description": "Single and batch prompt evaluation"},
        {"name": "Comparison", "description": "Model comparison endpoints"},
        {"name": "Human-in-the-Loop", "description": "Human rating submission and retrieval"},
        {"name": "Streaming", "description": "Real-time token streaming"},
        {"name": "Datasets", "description": "Evaluation dataset management"},
        {"name": "Utilities", "description": "Helper endpoints for models and styles"},
    ]
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - restrictive by default
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


# ============ Health Check ============

@app.get("/", tags=["Health"], summary="Root health check")
async def root():
    """
    Quick health check endpoint.
    
    Returns service status, version, and available features.
    """
    return {
        "status": "healthy",
        "service": "⚡ MistralMeter",
        "version": "2.0.0",
        "api_configured": runner is not None,
        "features": [
            "variance_analysis",
            "llm_as_judge",
            "human_in_the_loop",
            "model_comparison"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "runner": "ready" if runner else "not configured",
            "evaluator": "ready" if evaluator else "not configured"
        },
        "security": {
            "auth_enabled": AUTH_ENABLED,
            "rate_limiting": "active",
            "cors_origins": ALLOWED_ORIGINS
        }
    }


# ============ Evaluation Endpoints ============

@app.post("/evaluate", response_model=Union[EvalResult, EvalResultWithVariance], tags=["Evaluation"])
@limiter.limit("10/minute")
async def evaluate_prompt(request: EvalRequest, authenticated: bool = Depends(verify_api_key)):
    """
    Evaluate a single prompt with optional multi-run variance analysis.
    
    **Key Features:**
    - Separate judge model from evaluated model (reduces bias)
    - Multiple runs for capturing LLM stochasticity
    - Statistical analysis (mean, std_dev, p50, p95)
    
    **Single Run Example:**
    ```json
    {
        "prompt": {"prompt": "Explain transformers in simple terms"},
        "model": "mistral-small-latest",
        "judge_model": "mistral-large-latest"
    }
    ```
    
    **Multi-Run Variance Analysis:**
    ```json
    {
        "prompt": {"prompt": "Explain transformers in simple terms"},
        "model": "mistral-small-latest",
        "runs": 5
    }
    ```
    
    With `runs > 1`, returns variance statistics including std_dev and percentiles.
    """
    if not runner or not evaluator:
        raise HTTPException(
            status_code=503,
            detail="Service not configured. Set MISTRAL_API_KEY."
        )
    
    # Determine judge model (default to mistral-large for quality)
    judge_model = request.judge_model or MistralModel.MISTRAL_LARGE
    
    try:
        if request.runs == 1:
            # Single run - return simple result
            response_text, collector = await runner.run_prompt(
                prompt=request.prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                use_streaming=True  # Enable TTFT measurement
            )
            
            # Update evaluator judge model if different
            eval_instance = LLMEvaluator(
                api_key=evaluator.api_key,
                judge_model=judge_model.value
            )
            
            quality_score = await eval_instance.evaluate(
                prompt=request.prompt.prompt,
                response=response_text,
                expected_style=request.prompt.expected_style,
                reference_answer=request.prompt.reference_answer
            )
            collector.set_quality(quality_score)
            
            return EvalResult(
                prompt=request.prompt.prompt,
                model=request.model.value,
                judge_model=judge_model.value,
                response=response_text,
                metrics=collector.to_eval_metrics()
            )
        
        else:
            # Multi-run - return variance analysis
            responses = []
            collectors = []
            quality_scores = []
            
            eval_instance = LLMEvaluator(
                api_key=evaluator.api_key,
                judge_model=judge_model.value
            )
            
            for _ in range(request.runs):
                response_text, collector = await runner.run_prompt(
                    prompt=request.prompt,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    use_streaming=True  # Enable TTFT measurement
                )
                
                quality_score = await eval_instance.evaluate(
                    prompt=request.prompt.prompt,
                    response=response_text,
                    expected_style=request.prompt.expected_style,
                    reference_answer=request.prompt.reference_answer
                )
                
                responses.append(response_text)
                collectors.append(collector)
                quality_scores.append(quality_score)
            
            # Find best response
            best_idx = max(range(len(quality_scores)), key=lambda i: quality_scores[i].score)
            
            # Compute variance metrics
            variance_metrics = compute_variance_metrics(collectors, quality_scores)
            
            return EvalResultWithVariance(
                prompt=request.prompt.prompt,
                model=request.model.value,
                judge_model=judge_model.value,
                responses=responses,
                best_response=responses[best_idx],
                metrics=variance_metrics
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/batch", response_model=BatchEvalResult, tags=["Evaluation"])
@limiter.limit("5/minute")
async def evaluate_batch(request: BatchEvalRequest, authenticated: bool = Depends(verify_api_key)):
    """
    Evaluate multiple prompts in batch.
    
    Executes all prompts with controlled concurrency and returns:
    - Individual results for each prompt
    - Aggregated summary statistics
    
    Great for running evaluation datasets.
    """
    if not runner or not evaluator:
        raise HTTPException(
            status_code=503,
            detail="Service not configured. Set MISTRAL_API_KEY."
        )
    
    try:
        # Run all prompts
        results_data = await runner.run_batch(
            prompts=request.prompts,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Determine judge model
        judge_model = getattr(request, 'judge_model', None) or MistralModel.MISTRAL_LARGE
        eval_instance = LLMEvaluator(
            api_key=evaluator.api_key,
            judge_model=judge_model.value
        )
        
        # Evaluate each response
        results = []
        for prompt, (response_text, collector) in zip(request.prompts, results_data):
            quality_score = await eval_instance.evaluate(
                prompt=prompt.prompt,
                response=response_text,
                expected_style=prompt.expected_style,
                reference_answer=prompt.reference_answer
            )
            collector.set_quality(quality_score)
            
            results.append(EvalResult(
                prompt=prompt.prompt,
                model=request.model.value,
                judge_model=judge_model.value,
                response=response_text,
                metrics=collector.to_eval_metrics()
            ))
        
        # Aggregate metrics
        summary = aggregate_metrics([r.metrics for r in results])
        
        return BatchEvalResult(results=results, summary=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare", response_model=CompareResult, tags=["Comparison"])
@limiter.limit("8/minute")
async def compare_models(request: CompareRequest, authenticated: bool = Depends(verify_api_key)):
    """
    Compare two models on the same prompt.
    
    Runs the prompt on both models and provides:
    - Individual results for each model
    - Side-by-side metrics comparison
    - Winner determination based on quality/latency trade-off
    
    **Judge Model Separation:** Uses `judge_model` parameter to evaluate both
    responses with a separate model (default: mistral-large).
    
    Useful for deciding which model to use for your use case.
    """
    if not runner or not evaluator:
        raise HTTPException(
            status_code=503,
            detail="Service not configured. Set MISTRAL_API_KEY."
        )
    
    # Use separate judge model
    judge_model = request.judge_model or MistralModel.MISTRAL_LARGE
    eval_instance = LLMEvaluator(
        api_key=evaluator.api_key,
        judge_model=judge_model.value
    )
    
    try:
        # Run on both models
        response_a, collector_a = await runner.run_prompt(
            prompt=request.prompt,
            model=request.model_a,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        response_b, collector_b = await runner.run_prompt(
            prompt=request.prompt,
            model=request.model_b,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Evaluate both with separate judge
        quality_a = await eval_instance.evaluate(
            prompt=request.prompt.prompt,
            response=response_a,
            expected_style=request.prompt.expected_style
        )
        collector_a.set_quality(quality_a)
        
        quality_b = await eval_instance.evaluate(
            prompt=request.prompt.prompt,
            response=response_b,
            expected_style=request.prompt.expected_style
        )
        collector_b.set_quality(quality_b)
        
        # Build results
        result_a = EvalResult(
            prompt=request.prompt.prompt,
            model=request.model_a.value,
            judge_model=judge_model.value,
            response=response_a,
            metrics=collector_a.to_eval_metrics()
        )
        
        result_b = EvalResult(
            prompt=request.prompt.prompt,
            model=request.model_b.value,
            judge_model=judge_model.value,
            response=response_b,
            metrics=collector_b.to_eval_metrics()
        )
        
        # Compare metrics
        comparison = compare_metrics(
            collector_a.to_eval_metrics(),
            collector_b.to_eval_metrics()
        )
        
        # Determine winner
        winner = request.model_a.value if comparison["overall_winner"] == "a" else request.model_b.value
        
        summary = (
            f"{winner} wins with {comparison['confidence']}% confidence. "
            f"Quality: {comparison['quality']['a_score']:.1f} vs {comparison['quality']['b_score']:.1f}. "
            f"Latency: {comparison['latency']['a_ms']:.0f}ms vs {comparison['latency']['b_ms']:.0f}ms."
        )
        
        return CompareResult(
            prompt=request.prompt.prompt,
            model_a=result_a,
            model_b=result_b,
            winner=winner,
            comparison_summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Human-in-the-Loop Endpoints ============

# In-memory storage for human ratings (use Redis/DB in production)
human_ratings_store: dict[str, list[HumanRating]] = {}


@app.post("/rate/{evaluation_id}", response_model=HumanRating, tags=["Human-in-the-Loop"])
async def submit_human_rating(
    evaluation_id: str,
    rating: int = Query(..., ge=1, le=5, description="Human rating 1-5"),
    comment: Optional[str] = None,
    rater_id: Optional[str] = None
):
    """
    Submit a human rating for an evaluation result.
    
    **Human-in-the-Loop Evaluation:**
    - LLM-as-judge provides automated scores (can be biased)
    - Human ratings provide ground truth for correlation analysis
    - Compare human vs LLM scores to calibrate automated evaluation
    
    **Rating Scale:**
    - 1: Poor/Incorrect
    - 2: Below average
    - 3: Acceptable
    - 4: Good
    - 5: Excellent
    
    Returns the submitted rating for confirmation.
    """
    human_rating = HumanRating(
        evaluation_id=evaluation_id,
        rating=rating,
        comment=comment,
        rater_id=rater_id
    )
    
    # Store rating
    if evaluation_id not in human_ratings_store:
        human_ratings_store[evaluation_id] = []
    human_ratings_store[evaluation_id].append(human_rating)
    
    return human_rating


@app.get("/rate/{evaluation_id}", response_model=list[HumanRating], tags=["Human-in-the-Loop"])
async def get_human_ratings(evaluation_id: str):
    """
    Get all human ratings for an evaluation.
    
    Returns list of ratings submitted by different raters.
    Useful for computing inter-rater reliability (Krippendorff's alpha).
    """
    return human_ratings_store.get(evaluation_id, [])


@app.get("/ratings/stats", tags=["Human-in-the-Loop"])
async def get_rating_statistics():
    """
    Get aggregate statistics on human ratings.
    
    Returns:
    - Total evaluations rated
    - Average rating across all evaluations
    - Rating distribution
    """
    all_ratings = []
    for ratings in human_ratings_store.values():
        all_ratings.extend([r.rating for r in ratings])
    
    if not all_ratings:
        return {
            "total_evaluations": 0,
            "total_ratings": 0,
            "average_rating": None,
            "distribution": {}
        }
    
    from collections import Counter
    distribution = dict(Counter(all_ratings))
    
    return {
        "total_evaluations": len(human_ratings_store),
        "total_ratings": len(all_ratings),
        "average_rating": sum(all_ratings) / len(all_ratings),
        "distribution": {str(k): v for k, v in sorted(distribution.items())}
    }


# ============ Streaming Endpoint ============

@app.post("/stream", tags=["Streaming"])
@limiter.limit("15/minute")
async def stream_response(request: EvalRequest, authenticated: bool = Depends(verify_api_key)):
    """
    Stream response tokens in real-time.
    
    Returns a Server-Sent Events stream of response tokens.
    Useful for building real-time UIs.
    """
    if not runner:
        raise HTTPException(
            status_code=503,
            detail="Service not configured. Set MISTRAL_API_KEY."
        )
    
    async def generate():
        async for chunk in runner.stream_response(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# ============ Dataset Endpoints ============

DATASETS_DIR = Path(__file__).parent.parent / "datasets"


@app.get("/datasets", response_model=list[DatasetInfo], tags=["Datasets"])
async def list_datasets():
    """List available evaluation datasets."""
    datasets = []
    
    if DATASETS_DIR.exists():
        for file in DATASETS_DIR.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    prompts = data.get("prompts", [])
                    categories = list(set(
                        p.get("category", "uncategorized") 
                        for p in prompts
                    ))
                    
                    datasets.append(DatasetInfo(
                        name=file.stem,
                        description=data.get("description"),
                        prompt_count=len(prompts),
                        categories=categories
                    ))
            except:
                pass
    
    return datasets


@app.get("/datasets/{name}", response_model=EvalDataset, tags=["Datasets"])
async def get_dataset(name: str):
    """Get a specific dataset by name."""
    file_path = DATASETS_DIR / f"{name}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    
    try:
        with open(file_path) as f:
            data = json.load(f)
            return EvalDataset(
                name=name,
                description=data.get("description"),
                prompts=[EvalPrompt(**p) for p in data.get("prompts", [])]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/datasets/{name}/evaluate", response_model=BatchEvalResult, tags=["Datasets"])
@limiter.limit("3/minute")
async def evaluate_dataset(
    name: str,
    model: MistralModel = MistralModel.MISTRAL_SMALL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Evaluate an entire dataset.
    
    Runs all prompts in the dataset and returns aggregated results.
    """
    # Get dataset
    dataset = await get_dataset(name)
    
    # Create batch request
    batch_request = BatchEvalRequest(
        prompts=dataset.prompts,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return await evaluate_batch(batch_request)


# ============ Utility Endpoints ============

@app.get("/models", tags=["Utilities"])
async def list_models():
    """List available Mistral models."""
    return {
        "models": [
            {
                "id": model.value,
                "name": model.name,
                "description": _get_model_description(model)
            }
            for model in MistralModel
        ]
    }


@app.get("/styles", tags=["Utilities"])
async def list_styles():
    """List available response styles for evaluation."""
    return {
        "styles": [
            {
                "id": style.value,
                "name": style.name
            }
            for style in ExpectedStyle
        ]
    }


def _get_model_description(model: MistralModel) -> str:
    """Get description for a model."""
    descriptions = {
        MistralModel.MISTRAL_TINY: "Fastest, most cost-effective",
        MistralModel.MISTRAL_SMALL: "Good balance of speed and quality",
        MistralModel.MISTRAL_MEDIUM: "Higher quality, moderate cost",
        MistralModel.MISTRAL_LARGE: "Highest quality, highest cost",
        MistralModel.OPEN_MISTRAL_7B: "Open source 7B model",
        MistralModel.OPEN_MIXTRAL_8X7B: "Open source MoE model",
        MistralModel.OPEN_MIXTRAL_8X22B: "Large open source MoE model",
        MistralModel.CODESTRAL: "Specialized for code generation"
    }
    return descriptions.get(model, "Mistral model")


# ============ Run with uvicorn ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
