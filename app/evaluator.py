"""
LLM-as-a-Judge Evaluator module.

Uses a second LLM call to evaluate the quality of responses.
This is a key technique used in production LLM evaluation pipelines.

Evaluation criteria:
- Clarity: How clear and understandable is the response?
- Accuracy: How accurate and factually correct is the response?
- Completeness: How complete and comprehensive is the response?
- Relevance: How relevant is the response to the prompt?
- Style Match: How well does the response match the expected style?
"""

import os
import json
import re
from typing import Optional
from dotenv import load_dotenv
from mistralai import Mistral

from app.schemas import QualityScore, ExpectedStyle

load_dotenv()


# Evaluation prompt template - this is the core of LLM-as-judge
EVALUATION_PROMPT = """You are an expert evaluator of AI-generated responses. 
Your task is to evaluate the quality of a response given a prompt and expected style.

## Evaluation Criteria (score 0-10 for each):

1. **Clarity** (0-10): How clear, well-structured, and easy to understand is the response?
2. **Accuracy** (0-10): How accurate, factually correct, and reliable is the information?
3. **Completeness** (0-10): How complete and comprehensive is the response? Does it fully address the prompt?
4. **Relevance** (0-10): How relevant and on-topic is the response?
5. **Style Match** (0-10): How well does the response match the expected style: "{expected_style}"?

## Input

**Prompt:** {prompt}

**Expected Style:** {expected_style}

**Response to Evaluate:**
{response}

{reference_section}

## Output Format

Respond ONLY with a valid JSON object in this exact format:
{{
    "clarity": <score>,
    "accuracy": <score>,
    "completeness": <score>,
    "relevance": <score>,
    "style_match": <score>,
    "overall_score": <weighted_average>,
    "feedback": "<2-3 sentence summary of strengths and areas for improvement>"
}}

Be fair but critical. A score of 7-8 is good, 9-10 is exceptional.
"""


class LLMEvaluator:
    """
    Evaluates LLM responses using another LLM as a judge.
    
    This technique (LLM-as-judge) is widely used in production
    because it scales better than human evaluation while providing
    nuanced quality assessment.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        judge_model: str = "mistral-large-latest"
    ):
        """
        Initialize the evaluator.
        
        Args:
            api_key: Mistral API key
            judge_model: Model to use for evaluation (should be capable)
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key required")
        
        self.client = Mistral(api_key=self.api_key)
        self.judge_model = judge_model
    
    async def evaluate(
        self,
        prompt: str,
        response: str,
        expected_style: ExpectedStyle = ExpectedStyle.EDUCATIONAL,
        reference_answer: Optional[str] = None
    ) -> QualityScore:
        """
        Evaluate a response using LLM-as-judge.
        
        Args:
            prompt: Original prompt
            response: Response to evaluate
            expected_style: Expected response style
            reference_answer: Optional reference for comparison
        
        Returns:
            QualityScore with detailed breakdown
        """
        # Build reference section if provided
        reference_section = ""
        if reference_answer:
            reference_section = f"""
**Reference Answer (for comparison):**
{reference_answer}

Consider the reference when evaluating accuracy and completeness.
"""
        
        # Format evaluation prompt
        style_value = expected_style.value if hasattr(expected_style, 'value') else expected_style
        eval_prompt = EVALUATION_PROMPT.format(
            prompt=prompt,
            response=response,
            expected_style=style_value,
            reference_section=reference_section
        )
        
        # Call the judge model
        judge_response = await self.client.chat.complete_async(
            model=self.judge_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI response evaluator. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": eval_prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=500
        )
        
        # Parse the evaluation
        return self._parse_evaluation(judge_response.choices[0].message.content)
    
    def _parse_evaluation(self, eval_text: str) -> QualityScore:
        """Parse LLM evaluation output into QualityScore."""
        try:
            # Try to extract JSON from the response
            # Handle case where LLM wraps in markdown code blocks
            json_match = re.search(r'\{[^{}]*\}', eval_text, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
            else:
                eval_data = json.loads(eval_text)
            
            # Extract criteria scores
            criteria_scores = {
                "clarity": float(eval_data.get("clarity", 5)),
                "accuracy": float(eval_data.get("accuracy", 5)),
                "completeness": float(eval_data.get("completeness", 5)),
                "relevance": float(eval_data.get("relevance", 5)),
                "style_match": float(eval_data.get("style_match", 5))
            }
            
            # Get overall score (or calculate weighted average)
            if "overall_score" in eval_data:
                overall = float(eval_data["overall_score"])
            else:
                # Weighted average: accuracy and completeness weighted higher
                weights = {
                    "clarity": 0.15,
                    "accuracy": 0.30,
                    "completeness": 0.25,
                    "relevance": 0.15,
                    "style_match": 0.15
                }
                overall = sum(
                    criteria_scores[k] * weights[k] 
                    for k in criteria_scores
                )
            
            feedback = eval_data.get("feedback", "Evaluation completed.")
            
            return QualityScore(
                score=round(overall, 1),
                feedback=feedback,
                criteria_scores=criteria_scores
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback for parsing errors
            return QualityScore(
                score=5.0,
                feedback=f"Evaluation parsing error: {str(e)}. Raw: {eval_text[:200]}",
                criteria_scores={}
            )
    
    async def compare_responses(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        expected_style: ExpectedStyle = ExpectedStyle.EDUCATIONAL
    ) -> dict:
        """
        Compare two responses and determine which is better.
        
        Useful for A/B testing different models or configurations.
        """
        compare_prompt = f"""You are comparing two AI responses to the same prompt.

## Prompt
{prompt}

## Expected Style
{expected_style.value if hasattr(expected_style, 'value') else expected_style}

## Response A
{response_a}

## Response B
{response_b}

## Task
Compare these responses and determine which is better overall.

Respond with JSON:
{{
    "winner": "A" or "B" or "tie",
    "a_score": <0-10>,
    "b_score": <0-10>,
    "reasoning": "<brief explanation of why one is better>"
}}
"""
        
        judge_response = await self.client.chat.complete_async(
            model=self.judge_model,
            messages=[
                {"role": "user", "content": compare_prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        try:
            json_match = re.search(
                r'\{[^{}]*\}', 
                judge_response.choices[0].message.content, 
                re.DOTALL
            )
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "winner": "tie",
            "a_score": 5,
            "b_score": 5,
            "reasoning": "Could not parse comparison"
        }


class RubricEvaluator:
    """
    Alternative evaluator using predefined rubrics.
    
    More deterministic than LLM-as-judge but less flexible.
    Good for specific, well-defined evaluation criteria.
    """
    
    # Predefined rubrics for common evaluation scenarios
    RUBRICS = {
        "factual_qa": {
            "criteria": ["accuracy", "completeness", "citation"],
            "weights": [0.5, 0.3, 0.2]
        },
        "creative_writing": {
            "criteria": ["creativity", "coherence", "engagement"],
            "weights": [0.4, 0.3, 0.3]
        },
        "code_explanation": {
            "criteria": ["accuracy", "clarity", "examples"],
            "weights": [0.4, 0.35, 0.25]
        },
        "summarization": {
            "criteria": ["conciseness", "completeness", "accuracy"],
            "weights": [0.3, 0.35, 0.35]
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=self.api_key)
    
    async def evaluate_with_rubric(
        self,
        prompt: str,
        response: str,
        rubric_type: str = "factual_qa"
    ) -> QualityScore:
        """Evaluate using a predefined rubric."""
        if rubric_type not in self.RUBRICS:
            rubric_type = "factual_qa"
        
        rubric = self.RUBRICS[rubric_type]
        criteria_list = ", ".join(rubric["criteria"])
        
        eval_prompt = f"""Evaluate this response using these specific criteria: {criteria_list}

Prompt: {prompt}
Response: {response}

Score each criterion 0-10 and respond with JSON:
{{
    {', '.join(f'"{c}": <score>' for c in rubric["criteria"])},
    "feedback": "<brief feedback>"
}}
"""
        
        judge_response = await self.client.chat.complete_async(
            model="mistral-small-latest",  # Smaller model for rubric eval
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.1,
            max_tokens=200
        )
        
        try:
            json_match = re.search(
                r'\{[^{}]*\}',
                judge_response.choices[0].message.content,
                re.DOTALL
            )
            if json_match:
                data = json.loads(json_match.group())
                
                criteria_scores = {
                    c: float(data.get(c, 5)) 
                    for c in rubric["criteria"]
                }
                
                overall = sum(
                    criteria_scores[c] * w 
                    for c, w in zip(rubric["criteria"], rubric["weights"])
                )
                
                return QualityScore(
                    score=round(overall, 1),
                    feedback=data.get("feedback", ""),
                    criteria_scores=criteria_scores
                )
        except:
            pass
        
        return QualityScore(
            score=5.0,
            feedback="Rubric evaluation failed",
            criteria_scores={}
        )
