"""
Metrics calculation module for LLM evaluation.

Handles:
- Latency measurement with high precision
- Token counting and cost estimation
- Aggregation of metrics across batches
- Variance analysis for multiple runs (capturing LLM stochasticity)
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import Optional
from contextlib import contextmanager

from app.schemas import (
    TokenMetrics, 
    LatencyMetrics, 
    LatencyMetricsWithVariance,
    QualityScore,
    QualityScoreWithVariance, 
    EvalMetrics,
    EvalMetricsWithVariance
)


@dataclass
class MetricsCollector:
    """
    Collects and calculates metrics during LLM inference.
    
    Usage:
        collector = MetricsCollector()
        with collector.measure_latency():
            response = call_llm(...)
        collector.record_tokens(input_tokens=10, output_tokens=50)
    """
    
    # Timing
    _start_time: Optional[float] = field(default=None, repr=False)
    _end_time: Optional[float] = field(default=None, repr=False)
    _first_token_time: Optional[float] = field(default=None, repr=False)
    
    # Token counts
    input_tokens: int = 0
    output_tokens: int = 0
    
    # Quality (set after evaluation)
    quality_score: Optional[QualityScore] = None
    
    @contextmanager
    def measure_latency(self):
        """Context manager for measuring total latency."""
        self._start_time = time.perf_counter()
        try:
            yield self
        finally:
            self._end_time = time.perf_counter()
    
    def mark_first_token(self):
        """Mark when first token is received (for streaming)."""
        if self._first_token_time is None:
            self._first_token_time = time.perf_counter()
    
    def record_tokens(self, input_tokens: int, output_tokens: int):
        """Record token usage."""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
    
    def set_quality(self, score: QualityScore):
        """Set quality evaluation."""
        self.quality_score = score
    
    @property
    def total_latency_ms(self) -> float:
        """Total latency in milliseconds."""
        if self._start_time is None or self._end_time is None:
            return 0.0
        return (self._end_time - self._start_time) * 1000
    
    @property
    def time_to_first_token_ms(self) -> Optional[float]:
        """Time to first token in milliseconds."""
        if self._start_time is None or self._first_token_time is None:
            return None
        return (self._first_token_time - self._start_time) * 1000
    
    @property
    def tokens_per_second(self) -> Optional[float]:
        """Generation speed in tokens per second."""
        if self._start_time is None or self._end_time is None:
            return None
        duration_s = self._end_time - self._start_time
        if duration_s <= 0:
            return None
        return self.output_tokens / duration_s
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens
    
    def to_eval_metrics(self) -> EvalMetrics:
        """Convert collected data to EvalMetrics schema."""
        token_metrics = TokenMetrics(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.total_tokens
        )
        
        latency_metrics = LatencyMetrics(
            total_ms=round(self.total_latency_ms, 2),
            time_to_first_token_ms=(
                round(self.time_to_first_token_ms, 2) 
                if self.time_to_first_token_ms else None
            ),
            tokens_per_second=(
                round(self.tokens_per_second, 1)
                if self.tokens_per_second else None
            )
        )
        
        # Default quality if not evaluated
        quality = self.quality_score or QualityScore(
            score=0.0,
            feedback="Not evaluated",
            criteria_scores={}
        )
        
        return EvalMetrics(
            tokens=token_metrics,
            latency=latency_metrics,
            quality=quality
        )


def aggregate_metrics(metrics_list: list[EvalMetrics]) -> dict:
    """
    Aggregate metrics from multiple evaluations.
    
    Returns summary statistics for batch evaluation.
    """
    if not metrics_list:
        return {}
    
    n = len(metrics_list)
    
    # Latency stats
    latencies = [m.latency.total_ms for m in metrics_list]
    avg_latency = sum(latencies) / n
    min_latency = min(latencies)
    max_latency = max(latencies)
    
    # Token stats
    total_input = sum(m.tokens.input_tokens for m in metrics_list)
    total_output = sum(m.tokens.output_tokens for m in metrics_list)
    total_tokens = sum(m.tokens.total_tokens for m in metrics_list)
    avg_output_tokens = total_output / n
    
    # Quality stats
    quality_scores = [m.quality.score for m in metrics_list]
    avg_quality = sum(quality_scores) / n
    min_quality = min(quality_scores)
    max_quality = max(quality_scores)
    
    # Throughput
    total_time_s = sum(latencies) / 1000
    overall_throughput = total_output / total_time_s if total_time_s > 0 else 0
    
    return {
        "count": n,
        "latency": {
            "avg_ms": round(avg_latency, 2),
            "min_ms": round(min_latency, 2),
            "max_ms": round(max_latency, 2),
            "p50_ms": round(sorted(latencies)[n // 2], 2),
        },
        "tokens": {
            "total_input": total_input,
            "total_output": total_output,
            "total": total_tokens,
            "avg_output_per_prompt": round(avg_output_tokens, 1),
        },
        "quality": {
            "avg_score": round(avg_quality, 2),
            "min_score": round(min_quality, 2),
            "max_score": round(max_quality, 2),
        },
        "throughput": {
            "tokens_per_second": round(overall_throughput, 1),
        },
        "estimated_cost_usd": round(
            total_input * 0.000002 + total_output * 0.000006, 6
        )
    }


def compare_metrics(metrics_a: EvalMetrics, metrics_b: EvalMetrics) -> dict:
    """
    Compare metrics between two model runs.
    
    Returns comparison summary with winner determination.
    """
    comparison = {
        "latency": {
            "a_ms": metrics_a.latency.total_ms,
            "b_ms": metrics_b.latency.total_ms,
            "diff_ms": round(metrics_b.latency.total_ms - metrics_a.latency.total_ms, 2),
            "faster": "a" if metrics_a.latency.total_ms < metrics_b.latency.total_ms else "b"
        },
        "tokens": {
            "a_output": metrics_a.tokens.output_tokens,
            "b_output": metrics_b.tokens.output_tokens,
            "diff": metrics_b.tokens.output_tokens - metrics_a.tokens.output_tokens
        },
        "quality": {
            "a_score": metrics_a.quality.score,
            "b_score": metrics_b.quality.score,
            "diff": round(metrics_b.quality.score - metrics_a.quality.score, 2),
            "better": "a" if metrics_a.quality.score > metrics_b.quality.score else "b"
        }
    }
    
    # Determine overall winner (quality weighted more heavily)
    a_score = (
        (10 - metrics_a.latency.total_ms / 100) * 0.2 +  # Speed (normalized)
        metrics_a.quality.score * 0.8  # Quality
    )
    b_score = (
        (10 - metrics_b.latency.total_ms / 100) * 0.2 +
        metrics_b.quality.score * 0.8
    )
    
    comparison["overall_winner"] = "a" if a_score > b_score else "b"
    comparison["confidence"] = round(abs(a_score - b_score) / 10 * 100, 1)
    
    return comparison


def compute_variance_metrics(
    collectors: list["MetricsCollector"],
    quality_scores: list[QualityScore]
) -> EvalMetricsWithVariance:
    """
    Compute metrics with variance statistics from multiple evaluation runs.
    
    This captures the inherent stochasticity of LLM responses, which is
    crucial for reliable benchmarking.
    
    Args:
        collectors: List of MetricsCollector from each run
        quality_scores: List of QualityScore from each run
    
    Returns:
        EvalMetricsWithVariance with statistical analysis
    """
    n = len(collectors)
    if n == 0:
        raise ValueError("Need at least one run")
    
    # Token metrics (use first run - tokens are relatively deterministic)
    token_metrics = TokenMetrics(
        input_tokens=collectors[0].input_tokens,
        output_tokens=round(statistics.mean(c.output_tokens for c in collectors)),
        total_tokens=round(statistics.mean(c.total_tokens for c in collectors))
    )
    
    # Latency variance
    latencies = [c.total_latency_ms for c in collectors]
    ttfts = [c.time_to_first_token_ms for c in collectors if c.time_to_first_token_ms]
    tps_values = [c.tokens_per_second for c in collectors if c.tokens_per_second]
    
    sorted_latencies = sorted(latencies)
    
    latency_variance = LatencyMetricsWithVariance(
        mean_ms=round(statistics.mean(latencies), 2),
        std_dev_ms=round(statistics.stdev(latencies), 2) if n > 1 else 0.0,
        min_ms=round(min(latencies), 2),
        max_ms=round(max(latencies), 2),
        p50_ms=round(sorted_latencies[n // 2], 2),
        p95_ms=round(sorted_latencies[int(n * 0.95)], 2) if n >= 5 else None,
        mean_ttft_ms=round(statistics.mean(ttfts), 2) if ttfts else None,
        mean_tokens_per_second=round(statistics.mean(tps_values), 1) if tps_values else None,
        runs=n
    )
    
    # Quality variance
    scores = [q.score for q in quality_scores]
    feedbacks = [q.feedback for q in quality_scores]
    
    # Aggregate criteria scores
    all_criteria = {}
    for q in quality_scores:
        for criterion, score in q.criteria_scores.items():
            if criterion not in all_criteria:
                all_criteria[criterion] = []
            all_criteria[criterion].append(score)
    
    criteria_means = {
        criterion: round(statistics.mean(values), 2)
        for criterion, values in all_criteria.items()
    }
    
    quality_variance = QualityScoreWithVariance(
        mean_score=round(statistics.mean(scores), 2),
        std_dev=round(statistics.stdev(scores), 2) if n > 1 else 0.0,
        min_score=round(min(scores), 2),
        max_score=round(max(scores), 2),
        runs=n,
        criteria_means=criteria_means,
        feedbacks=feedbacks
    )
    
    return EvalMetricsWithVariance(
        tokens=token_metrics,
        latency=latency_variance,
        quality=quality_variance
    )


def calculate_percentile(values: list[float], percentile: float) -> float:
    """Calculate the given percentile of a list of values."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]
