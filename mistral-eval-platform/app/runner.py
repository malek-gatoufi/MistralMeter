"""
Prompt Runner module for executing prompts against Mistral models.

Handles:
- Single prompt execution
- Batch execution with concurrency control
- Streaming support
- Error handling and retries
"""

import os
import asyncio
from typing import AsyncIterator, Optional
from dotenv import load_dotenv
from mistralai import Mistral

from app.schemas import (
    EvalPrompt, 
    MistralModel, 
    EvalResult,
    EvalMetrics
)
from app.metrics import MetricsCollector

# Load environment variables
load_dotenv()


class MistralRunner:
    """
    Executes prompts against Mistral API and collects metrics.
    
    Features:
    - Sync and async execution
    - Streaming support for TTFT measurement
    - Automatic metrics collection
    - Retry logic for resilience
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the runner with API credentials.
        
        Args:
            api_key: Mistral API key. Falls back to MISTRAL_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Mistral API key required. Set MISTRAL_API_KEY env var or pass api_key."
            )
        self.client = Mistral(api_key=self.api_key)
    
    async def run_prompt(
        self,
        prompt: EvalPrompt,
        model: MistralModel = MistralModel.MISTRAL_SMALL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        use_streaming: bool = True  # Enabled to capture TTFT metrics
    ) -> tuple[str, MetricsCollector]:
        """
        Execute a single prompt and collect metrics.
        
        Args:
            prompt: The evaluation prompt to run
            model: Mistral model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_streaming: Whether to use streaming (for TTFT measurement)
        
        Returns:
            Tuple of (response_text, metrics_collector)
        """
        collector = MetricsCollector()
        
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(prompt.expected_style)
            },
            {
                "role": "user",
                "content": prompt.prompt
            }
        ]
        
        if use_streaming:
            response_text = await self._run_streaming(
                messages, model, temperature, max_tokens, collector
            )
        else:
            response_text = await self._run_sync(
                messages, model, temperature, max_tokens, collector
            )
        
        return response_text, collector
    
    async def _run_streaming(
        self,
        messages: list[dict],
        model: MistralModel,
        temperature: float,
        max_tokens: int,
        collector: MetricsCollector
    ) -> str:
        """Execute with streaming to measure TTFT."""
        response_chunks = []
        
        with collector.measure_latency():
            async for chunk in self.client.chat.stream_async(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                # Mark first token
                if not response_chunks:
                    collector.mark_first_token()
                
                if chunk.data.choices and len(chunk.data.choices) > 0 and chunk.data.choices[0].delta.content:
                    response_chunks.append(chunk.data.choices[0].delta.content)
            
            # Get final usage from last chunk  
            if hasattr(chunk.data, 'usage') and chunk.data.usage:
                collector.record_tokens(
                    input_tokens=chunk.data.usage.prompt_tokens,
                    output_tokens=chunk.data.usage.completion_tokens
                )
        
        return "".join(response_chunks)
    
    async def _run_sync(
        self,
        messages: list[dict],
        model: MistralModel,
        temperature: float,
        max_tokens: int,
        collector: MetricsCollector
    ) -> str:
        """Execute without streaming."""
        with collector.measure_latency():
            response = await self.client.chat.complete_async(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        collector.record_tokens(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens
        )
        
        return response.choices[0].message.content
    
    async def run_batch(
        self,
        prompts: list[EvalPrompt],
        model: MistralModel = MistralModel.MISTRAL_SMALL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        concurrency: int = 3
    ) -> list[tuple[str, MetricsCollector]]:
        """
        Execute multiple prompts with controlled concurrency.
        
        Args:
            prompts: List of prompts to evaluate
            model: Mistral model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
            concurrency: Max concurrent requests
        
        Returns:
            List of (response_text, metrics_collector) tuples
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def run_with_semaphore(prompt: EvalPrompt):
            async with semaphore:
                return await self.run_prompt(
                    prompt, model, temperature, max_tokens
                )
        
        tasks = [run_with_semaphore(p) for p in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error on prompt {i}: {result}")
                # Create a failed result
                collector = MetricsCollector()
                collector.record_tokens(0, 0)
                valid_results.append((f"Error: {result}", collector))
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def stream_response(
        self,
        prompt: EvalPrompt,
        model: MistralModel = MistralModel.MISTRAL_SMALL,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        """
        Stream response tokens for real-time display.
        
        Yields individual tokens/chunks as they arrive.
        """
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(prompt.expected_style)
            },
            {
                "role": "user",
                "content": prompt.prompt
            }
        ]
        
        async for chunk in self.client.chat.stream_async(
            model=model.value,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            if chunk.data.choices and len(chunk.data.choices) > 0 and chunk.data.choices[0].delta.content:
                yield chunk.data.choices[0].delta.content
    
    def _get_system_prompt(self, style) -> str:
        """Get system prompt based on expected style."""
        style_prompts = {
            "educational": (
                "You are a helpful educational assistant. Provide clear, "
                "well-structured explanations that are easy to understand. "
                "Use examples when helpful."
            ),
            "technical": (
                "You are a technical expert. Provide precise, accurate, "
                "and detailed technical information. Include relevant "
                "technical terms and specifications."
            ),
            "concise": (
                "You are a concise assistant. Provide brief, to-the-point "
                "answers. Avoid unnecessary elaboration while ensuring "
                "completeness."
            ),
            "creative": (
                "You are a creative assistant. Provide imaginative, "
                "engaging, and original responses. Feel free to be playful "
                "with language."
            ),
            "formal": (
                "You are a professional assistant. Provide formal, "
                "well-structured responses suitable for business or "
                "academic contexts."
            ),
            "conversational": (
                "You are a friendly conversational assistant. Provide "
                "natural, engaging responses as if chatting with a friend."
            )
        }
        
        # Handle both string and enum
        style_key = style.value if hasattr(style, 'value') else style
        return style_prompts.get(style_key, style_prompts["educational"])


# Utility function for simple usage
async def quick_eval(
    prompt: str,
    model: str = "mistral-small-latest",
    api_key: Optional[str] = None
) -> dict:
    """
    Quick evaluation of a single prompt.
    
    Example:
        result = await quick_eval("What is machine learning?")
        print(result["response"])
        print(result["metrics"])
    """
    runner = MistralRunner(api_key=api_key)
    eval_prompt = EvalPrompt(prompt=prompt)
    
    # Convert string model to enum if needed
    model_enum = MistralModel(model) if isinstance(model, str) else model
    
    response, collector = await runner.run_prompt(eval_prompt, model=model_enum)
    
    return {
        "prompt": prompt,
        "response": response,
        "metrics": {
            "latency_ms": collector.total_latency_ms,
            "ttft_ms": collector.time_to_first_token_ms,
            "input_tokens": collector.input_tokens,
            "output_tokens": collector.output_tokens,
            "tokens_per_second": collector.tokens_per_second
        }
    }
