"""
Pydantic schemas for the Mistral Evaluation Platform.

Defines data models for:
- Evaluation prompts and datasets
- Metrics and results (with variance support)
- Human-in-the-loop ratings
- API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ExpectedStyle(str, Enum):
    """Expected response styles for evaluation."""
    EDUCATIONAL = "educational"
    TECHNICAL = "technical"
    CONCISE = "concise"
    CREATIVE = "creative"
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"


class MistralModel(str, Enum):
    """Available Mistral models for evaluation."""
    MISTRAL_TINY = "mistral-tiny"
    MISTRAL_SMALL = "mistral-small-latest"
    MISTRAL_MEDIUM = "mistral-medium-latest"
    MISTRAL_LARGE = "mistral-large-latest"
    OPEN_MISTRAL_7B = "open-mistral-7b"
    OPEN_MIXTRAL_8X7B = "open-mixtral-8x7b"
    OPEN_MIXTRAL_8X22B = "open-mixtral-8x22b"
    CODESTRAL = "codestral-latest"


# ============ Human-in-the-loop ============

class HumanRating(BaseModel):
    """
    Human rating for calibrating LLM-as-judge.
    
    Human scores can be used to identify bias in automated evaluation
    and improve the judge model over time.
    """
    score: float = Field(..., ge=0.0, le=10.0, description="Human quality score 0-10")
    comment: Optional[str] = Field(default=None, description="Human feedback comment")
    rater_id: Optional[str] = Field(default=None, description="Identifier for the human rater")


# ============ Input Schemas ============

class EvalPrompt(BaseModel):
    """A single prompt for evaluation."""
    prompt: str = Field(..., description="The prompt text to evaluate")
    expected_style: ExpectedStyle = Field(
        default=ExpectedStyle.EDUCATIONAL,
        description="Expected response style"
    )
    reference_answer: Optional[str] = Field(
        default=None,
        description="Optional reference answer for comparison"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category/tag for grouping prompts"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Explain transformers in simple terms",
                    "expected_style": "educational",
                    "category": "ml_concepts"
                }
            ]
        }
    }


class EvalRequest(BaseModel):
    """Request to evaluate a single prompt."""
    prompt: EvalPrompt
    model: MistralModel = Field(
        default=MistralModel.MISTRAL_SMALL,
        description="Mistral model to evaluate"
    )
    judge_model: Optional[MistralModel] = Field(
        default=None,
        description="Model to use as judge (defaults to mistral-large). Separating judge from evaluated model reduces bias."
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=1024,
        ge=1,
        le=4096,
        description="Maximum tokens in response"
    )
    runs: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of evaluation runs for variance analysis"
    )


class BatchEvalRequest(BaseModel):
    """Request to evaluate multiple prompts."""
    prompts: list[EvalPrompt] = Field(..., min_length=1)
    model: MistralModel = Field(default=MistralModel.MISTRAL_SMALL)
    judge_model: Optional[MistralModel] = Field(default=None)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    runs: int = Field(default=1, ge=1, le=10)


class CompareRequest(BaseModel):
    """Request to compare two models on the same prompt."""
    prompt: EvalPrompt
    model_a: MistralModel = Field(default=MistralModel.MISTRAL_SMALL)
    model_b: MistralModel = Field(default=MistralModel.MISTRAL_LARGE)
    judge_model: Optional[MistralModel] = Field(
        default=None,
        description="Model to use as judge (defaults to mistral-large)"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    runs: int = Field(default=1, ge=1, le=10)


# ============ Variance Statistics ============

class VarianceStats(BaseModel):
    """Statistics for capturing LLM response variance across multiple runs."""
    mean: float = Field(..., description="Mean value across runs")
    std_dev: float = Field(..., description="Standard deviation")
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    p50: float = Field(..., description="50th percentile (median)")
    p95: Optional[float] = Field(default=None, description="95th percentile (requires 5+ runs)")
    runs: int = Field(..., description="Number of runs")


# ============ Output Schemas ============

class TokenMetrics(BaseModel):
    """Token usage metrics."""
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    total_tokens: int = Field(..., description="Total tokens used")
    
    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost based on typical Mistral pricing."""
        # Approximate pricing (varies by model)
        input_cost = self.input_tokens * 0.000002
        output_cost = self.output_tokens * 0.000006
        return round(input_cost + output_cost, 6)


class LatencyMetrics(BaseModel):
    """Latency metrics."""
    total_ms: float = Field(..., description="Total response time in ms")
    time_to_first_token_ms: Optional[float] = Field(
        default=None,
        description="Time to first token (streaming)"
    )
    tokens_per_second: Optional[float] = Field(
        default=None,
        description="Generation speed"
    )


class LatencyMetricsWithVariance(BaseModel):
    """Latency metrics with variance across multiple runs."""
    mean_ms: float = Field(..., description="Mean latency in ms")
    std_dev_ms: float = Field(..., description="Standard deviation")
    min_ms: float = Field(..., description="Minimum latency")
    max_ms: float = Field(..., description="Maximum latency")
    p50_ms: float = Field(..., description="Median latency")
    p95_ms: Optional[float] = Field(default=None, description="95th percentile")
    mean_ttft_ms: Optional[float] = Field(default=None, description="Mean time to first token")
    mean_tokens_per_second: Optional[float] = Field(default=None, description="Mean generation speed")
    runs: int = Field(..., description="Number of runs")


class QualityScore(BaseModel):
    """Quality evaluation from LLM-as-judge."""
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score 0-10")
    feedback: str = Field(..., description="Detailed feedback")
    criteria_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown by evaluation criteria"
    )


class QualityScoreWithVariance(BaseModel):
    """Quality score with variance across multiple runs."""
    mean_score: float = Field(..., description="Mean quality score")
    std_dev: float = Field(..., description="Standard deviation of quality")
    min_score: float = Field(..., description="Minimum score")
    max_score: float = Field(..., description="Maximum score")
    runs: int = Field(..., description="Number of runs")
    criteria_means: dict[str, float] = Field(
        default_factory=dict,
        description="Mean scores per criterion"
    )
    feedbacks: list[str] = Field(
        default_factory=list,
        description="All feedback from runs"
    )


class EvalMetrics(BaseModel):
    """Complete metrics for an evaluation."""
    tokens: TokenMetrics
    latency: LatencyMetrics
    quality: QualityScore


class EvalMetricsWithVariance(BaseModel):
    """Complete metrics with variance from multiple runs."""
    tokens: TokenMetrics  # Token counts are deterministic
    latency: LatencyMetricsWithVariance
    quality: QualityScoreWithVariance


class EvalResult(BaseModel):
    """Complete result for a single prompt evaluation."""
    prompt: str
    model: str
    judge_model: str = Field(default="mistral-large-latest")
    response: str
    metrics: EvalMetrics
    human_rating: Optional[HumanRating] = Field(
        default=None,
        description="Optional human rating for calibration"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Explain transformers in simple terms",
                    "model": "mistral-small-latest",
                    "response": "Transformers are a type of neural network...",
                    "metrics": {
                        "tokens": {
                            "input_tokens": 23,
                            "output_tokens": 214,
                            "total_tokens": 237
                        },
                        "latency": {
                            "total_ms": 812,
                            "tokens_per_second": 263.5
                        },
                        "quality": {
                            "score": 8.6,
                            "feedback": "Clear, well structured, accurate",
                            "criteria_scores": {
                                "clarity": 9.0,
                                "accuracy": 8.5,
                                "completeness": 8.3
                            }
                        }
                    }
                }
            ]
        }
    }


class BatchEvalResult(BaseModel):
    """Results for batch evaluation."""
    results: list[EvalResult]
    summary: dict = Field(
        default_factory=dict,
        description="Aggregated statistics"
    )


class EvalResultWithVariance(BaseModel):
    """Result with variance from multiple runs - captures LLM stochasticity."""
    prompt: str
    model: str
    judge_model: str = Field(default="mistral-large-latest")
    responses: list[str] = Field(..., description="All responses from runs")
    best_response: str = Field(..., description="Response with highest quality score")
    metrics: EvalMetricsWithVariance
    human_rating: Optional[HumanRating] = Field(
        default=None,
        description="Optional human rating for calibration"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Explain transformers in simple terms",
                    "model": "mistral-small-latest",
                    "judge_model": "mistral-large-latest",
                    "responses": ["Response 1...", "Response 2..."],
                    "best_response": "Response with highest score...",
                    "metrics": {
                        "tokens": {"input_tokens": 23, "output_tokens": 214, "total_tokens": 237},
                        "latency": {
                            "mean_ms": 812,
                            "std_dev_ms": 110,
                            "min_ms": 650,
                            "max_ms": 1023,
                            "p50_ms": 790,
                            "p95_ms": 1023,
                            "runs": 5
                        },
                        "quality": {
                            "mean_score": 8.4,
                            "std_dev": 0.6,
                            "min_score": 7.5,
                            "max_score": 9.2,
                            "runs": 5
                        }
                    }
                }
            ]
        }
    }


class CompareResult(BaseModel):
    """Results from model comparison."""
    prompt: str
    model_a: EvalResult
    model_b: EvalResult
    winner: Optional[str] = Field(
        default=None,
        description="Better performing model"
    )
    comparison_summary: str = Field(
        default="",
        description="Summary of differences"
    )


# ============ Dataset Schemas ============

class EvalDataset(BaseModel):
    """A dataset of evaluation prompts."""
    name: str
    description: Optional[str] = None
    prompts: list[EvalPrompt]
    
    @property
    def size(self) -> int:
        return len(self.prompts)


class DatasetInfo(BaseModel):
    """Info about available datasets."""
    name: str
    description: Optional[str]
    prompt_count: int
    categories: list[str]
