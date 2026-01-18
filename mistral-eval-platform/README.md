# ⚡ MistralMeter

<div align="center">

**Production-Grade LLM Evaluation Platform for Mistral AI**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3-00DC82.svg)](https://nuxt.com)
[![Mistral AI](https://img.shields.io/badge/Mistral-AI-FF7000.svg)](https://mistral.ai)
[![Podman](https://img.shields.io/badge/Podman-Ready-892CA0.svg)](https://podman.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Why This is Hard](#-why-llm-evaluation-is-hard) • [Design Principles](#-design-principles) • [Quick Start](#-quick-start) • [Internship Scope](#-internship-scope)

</div>

<p align="center">
  <img src="https://via.placeholder.com/800x450/0f172a/f97316?text=⚡+MistralMeter" alt="MistralMeter Screenshot" />
</p>

---

## 🎯 What is this?

**MistralMeter** is a production-ready API and dashboard for evaluating LLM performance. It measures what actually matters in real-world deployments:

- ⚡ **Latency** (total time, time to first token)
- 📊 **Token usage** (input/output, tokens/second)
- 🧠 **Response quality** (AI-evaluated with detailed feedback)
- 📈 **Variance analysis** (multiple runs, statistical confidence)
- 👤 **Human-in-the-loop** (calibrate automated scores with human judgment)

> *"MistralMeter explores how to evaluate LLM trade-offs in real-world conditions while accounting for model stochasticity."*

---

## 🧠 Why LLM Evaluation is Hard

Evaluating LLMs in production is non-trivial due to:

| Challenge | Why it matters |
|-----------|----------------|
| **Non-deterministic outputs** | Same prompt → different responses. Single runs are meaningless. |
| **Latency vs Quality vs Cost** | Faster models are cheaper but often worse. How do you choose? |
| **Judge bias** | LLMs rating themselves tend to score high. Self-evaluation is unreliable. |
| **Offline ≠ Online** | High benchmark scores don't guarantee user satisfaction. |
| **Variance across runs** | A model that scores 9/10 once might score 5/10 next time. |

**MistralMeter makes these trade-offs explicit rather than hidden.**

It doesn't pretend evaluation is simple—it gives you the tools to understand *why* a model behaves the way it does.

---

## 🎨 Design Principles

This project follows key evaluation best practices:

### 1. **Judge Model ≠ Evaluated Model**
The model being evaluated is **never** the same as the model judging quality. This prevents self-serving bias where a model rates its own outputs highly.

```python
# Example: Evaluate mistral-small, judge with mistral-large
POST /evaluate
{
  "model": "mistral-small-latest",      # Model being evaluated
  "judge_model": "mistral-large-latest" # Separate judge model
}
```

### 2. **Metrics Independent from Provider**
Latency, token counts, and quality criteria are measured using provider-agnostic techniques:
- Sub-millisecond timing with `time.perf_counter()`
- Token counting from response metadata
- Quality evaluation via structured prompts (portable to any LLM)

### 3. **Variance-Aware Benchmarking**
LLMs are inherently stochastic. A single run doesn't tell the full story.

```python
# Run 5 evaluations, get statistical analysis
POST /evaluate
{
  "prompt": {"prompt": "Explain transformers"},
  "model": "mistral-small-latest",
  "runs": 5
}

# Response includes variance metrics:
{
  "metrics": {
    "latency": {
      "mean": 850.2,
      "std_dev": 42.3,
      "p50": 843.0,
      "p95": 912.5
    },
    "quality": {
      "mean": 8.2,
      "std_dev": 0.4,
      "p50": 8.3,
      "p95": 8.7
    }
  }
}
```

### 4. **Human-in-the-Loop Calibration**
LLM-as-judge is useful but imperfect. Human ratings provide ground truth for:
- Validating automated scores
- Identifying systematic biases
- Computing human-LLM correlation

```python
# Submit human rating for evaluation
POST /rate/{evaluation_id}?rating=4&comment="Good but verbose"
```

---

## ✨ Features

### 🔬 Single Prompt Evaluation
Test individual prompts with comprehensive metrics and quality scoring.

### 📦 Batch Evaluation
Evaluate entire datasets with aggregated statistics (p50 latency, avg quality, cost estimation).

### ⚔️ Model Comparison
Side-by-side comparison of different Mistral models on the same prompt.

### 🤖 LLM-as-Judge
Automated quality evaluation using a **separate** LLM - prevents self-evaluation bias.

### 📈 Variance Analysis
Multiple runs per prompt with statistical analysis (mean, std_dev, p50, p95).

### 👤 Human Ratings
Submit and track human ratings to calibrate automated evaluation.

### 🌊 Streaming Support
Real-time token streaming with Server-Sent Events for building responsive UIs.

---

## 🚀 Quick Start

### 1. Clone and setup

```bash
cd mistral-eval-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your Mistral API key
```

Get your API key at [console.mistral.ai](https://console.mistral.ai)

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

### 4. Try it out

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

---

## 🐳 Docker / Podman

Run the entire stack with a single command:

### Quick Start (Podman)

```bash
# Create .env file with your API key
echo "MISTRAL_API_KEY=your_key_here" > .env

# Start all services
podman-compose up -d

# Or with Docker
docker-compose up -d
```

**Services:**
| Service | Port | URL |
|---------|------|-----|
| 🖥️ Dashboard | 3000 | http://localhost:3000 |
| 🔌 API | 8000 | http://localhost:8000/docs |

### Commands

```bash
# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Rebuild after changes
podman-compose up -d --build
```

### Individual Containers

```bash
# Build backend only
podman build -f backend.Dockerfile -t mistralmeter-api .

# Build frontend only
podman build -f frontend.Dockerfile -t mistralmeter-dashboard .

# Run backend manually
podman run -d -p 8000:8000 -e MISTRAL_API_KEY=$MISTRAL_API_KEY mistralmeter-api
```

---

## 🎨 Frontend

A beautiful **Nuxt 3 + Tailwind CSS** dashboard is included!

### Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the dashboard.

### Frontend Features

- 🎯 **Dashboard** - Overview of models, datasets, and quick actions
- 🔬 **Single Evaluation** - Test prompts with real-time quality scoring
- ⚔️ **Model Comparison** - Side-by-side A/B testing with visual charts
- 📊 **Batch Evaluation** - Run datasets with aggregated statistics
- 📁 **Dataset Browser** - View and manage evaluation datasets

### Screenshots

<details>
<summary>📸 Click to see screenshots</summary>

**Dashboard**
- Clean overview with API status, available models, and datasets
- Quick action cards for evaluation, comparison, and batch testing

**Evaluation Page**
- Interactive prompt editor with model/style selection
- Real-time quality score ring with criteria breakdown
- Detailed latency and token metrics

**Comparison Page**
- Side-by-side model responses
- Visual comparison bars for quality, latency, and tokens
- Winner determination with confidence score

</details>

---

## 📖 API Reference

### `POST /evaluate`
Evaluate a single prompt with full metrics and optional variance analysis.

```bash
# Simple evaluation
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "prompt": "Explain transformers in simple terms",
      "expected_style": "educational"
    },
    "model": "mistral-small-latest",
    "judge_model": "mistral-large-latest"
  }'
```

```bash
# Multi-run variance analysis
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "prompt": "Explain transformers in simple terms"
    },
    "model": "mistral-small-latest",
    "runs": 5
  }'
```

**Response (single run):**
```json
{
  "prompt": "Explain transformers in simple terms",
  "model": "mistral-small-latest",
  "judge_model": "mistral-large-latest",
  "response": "Transformers are a type of neural network architecture...",
  "metrics": {
    "tokens": {
      "input_tokens": 23,
      "output_tokens": 214,
      "total_tokens": 237
    },
    "latency": {
      "total_ms": 812.5,
      "time_to_first_token_ms": 156.3,
      "tokens_per_second": 263.5
    },
    "quality": {
      "score": 8.6,
      "feedback": "Clear, well-structured, accurate explanation",
      "criteria_scores": {
        "clarity": 9.0,
        "accuracy": 8.5,
        "completeness": 8.3,
        "relevance": 8.8,
        "style_match": 8.4
      }
    }
  }
}
```

**Response (multi-run with variance):**
```json
{
  "prompt": "Explain transformers in simple terms",
  "model": "mistral-small-latest",
  "judge_model": "mistral-large-latest",
  "responses": ["Response 1...", "Response 2...", ...],
  "best_response": "Response 2...",
  "metrics": {
    "latency": {
      "total_ms": {"mean": 850.2, "std_dev": 42.3, "p50": 843.0, "p95": 912.5},
      "time_to_first_token_ms": {"mean": 156.0, "std_dev": 12.1, "p50": 154.0, "p95": 175.0},
      "tokens_per_second": {"mean": 263.5, "std_dev": 15.2, "p50": 265.0, "p95": 285.0}
    },
    "quality": {
      "score": {"mean": 8.2, "std_dev": 0.4, "p50": 8.3, "p95": 8.7}
    }
  }
}
```

### `POST /evaluate/batch`
Evaluate multiple prompts with summary statistics.

### `POST /compare`
Compare two models on the same prompt with separate judge.

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "prompt": "Write a Python function for binary search"
    },
    "model_a": "mistral-small-latest",
    "model_b": "mistral-large-latest",
    "judge_model": "mistral-large-latest"
  }'
```

### `POST /rate/{evaluation_id}`
Submit a human rating for an evaluation.

```bash
curl -X POST "http://localhost:8000/rate/eval_123?rating=4&comment=Good%20but%20verbose"
```

### `GET /rate/{evaluation_id}`
Get all human ratings for an evaluation.

### `GET /ratings/stats`
Get aggregate statistics on human ratings.

### `POST /stream`
Stream response tokens in real-time (SSE).

### `GET /datasets`
List available evaluation datasets.

### `POST /datasets/{name}/evaluate`
Run evaluation on an entire dataset.

---
    "model_a": "mistral-small-latest",
    "model_b": "mistral-large-latest"
  }'
```

### `POST /stream`
Stream response tokens in real-time (SSE).

### `GET /datasets`
List available evaluation datasets.

### `POST /datasets/{name}/evaluate`
Run evaluation on an entire dataset.

---

## 🏗️ Architecture

```
mistral-eval-platform/
│
├── app/                      # Backend API (FastAPI)
│   ├── main.py               # FastAPI application & endpoints
│   ├── runner.py             # Prompt execution with metrics
│   ├── metrics.py            # Latency, tokens, aggregation
│   ├── evaluator.py          # LLM-as-judge quality evaluation
│   └── schemas.py            # Pydantic models
│
├── frontend/                 # Frontend (Nuxt 3 + Tailwind)
│   ├── pages/                # Vue pages
│   │   ├── index.vue         # Dashboard
│   │   ├── evaluate.vue      # Single evaluation
│   │   ├── compare.vue       # Model comparison
│   │   ├── batch.vue         # Batch evaluation
│   │   └── datasets.vue      # Dataset browser
│   ├── components/           # Reusable Vue components
│   ├── composables/          # Vue composables (API client)
│   ├── layouts/              # Page layouts
│   └── assets/               # CSS & static assets
│
├── datasets/
│   ├── qa_small.json         # General Q&A test set
│   └── coding_challenges.json # Code generation tests
│
├── requirements.txt
├── .env.example
└── README.md
```

### Key Components

| Module | Purpose |
|--------|---------|
| `runner.py` | Executes prompts against Mistral API with streaming support |
| `metrics.py` | High-precision latency measurement, token counting |
| `evaluator.py` | LLM-as-judge implementation for quality scoring |
| `schemas.py` | Type-safe data models with Pydantic |

---

## 🧠 Technical Highlights

### LLM-as-Judge Evaluation
Uses a secondary LLM call to evaluate response quality across 5 criteria:
- **Clarity**: Structure and understandability
- **Accuracy**: Factual correctness
- **Completeness**: Comprehensive coverage
- **Relevance**: On-topic responses
- **Style Match**: Adherence to expected style

### Metrics Collection
- Sub-millisecond precision timing with `time.perf_counter()`
- Time-to-first-token (TTFT) measurement via streaming
- Tokens-per-second throughput calculation
- Cost estimation based on token usage

### Batch Processing
- Controlled concurrency with semaphores
- Aggregated statistics (p50 latency, averages)
- Error handling per-prompt without failing batch

---

## 📊 Example Use Cases

### 1. Benchmark Different Models
```python
# Compare mistral-small vs mistral-large for your use case
POST /compare with the same prompt on both models
```

### 2. Evaluate a Prompt Dataset
```python
# Run your test suite through the API
POST /datasets/qa_small/evaluate?model=mistral-small-latest
```

### 3. Monitor Production Quality
```python
# Sample production prompts and track quality over time
POST /evaluate with real user queries
```

---

## 🎓 Why This Matters

This project demonstrates understanding of:

- ✅ **LLMs in production** - Real metrics that matter
- ✅ **Trade-offs** - Quality vs latency vs cost
- ✅ **Evaluation at scale** - LLM-as-judge techniques
- ✅ **Stochasticity handling** - Variance analysis for reliable benchmarks
- ✅ **Human calibration** - Recognizing LLM limitations
- ✅ **Developer tools** - Clean APIs with great DX
- ✅ **Modern Python** - FastAPI, Pydantic, async/await

> This is exactly what production LLM teams build internally.

---

## ⚠️ Known Limitations

Being transparent about limitations shows engineering maturity:

### 1. **LLM-as-Judge Bias**
Even with model separation, LLM judges can have systematic biases:
- Prefer longer responses (verbosity bias)
- Favor certain writing styles
- Miss domain-specific errors

**Mitigation:** Human-in-the-loop ratings for calibration.

### 2. **Approximate Cost Estimation**
Token-based cost estimates are approximations:
- Actual pricing varies by model version
- API pricing can change
- Doesn't account for rate limiting overhead

### 3. **In-Memory Storage**
Human ratings stored in memory (not persistent):
- Production would use Redis/PostgreSQL
- Designed for demonstration purposes

### 4. **No Prompt Versioning**
Prompt history not tracked:
- No A/B testing across prompt versions
- No drift detection over time

### 5. **Single-Region Testing**
Latency measurements reflect single-region performance:
- Multi-region deployment would show different latencies
- Network conditions vary

---

## 🔮 Future Work

Ideas for extending this platform:

### Near-term
- [ ] **Persistent storage** - PostgreSQL/Redis for ratings and results
- [ ] **Prompt versioning** - Track changes and compare versions
- [ ] **Export capabilities** - CSV/JSON export for analysis
- [ ] **Authentication** - API keys for multi-tenant usage

### Medium-term
- [ ] **Dashboard improvements** - Charts, trends, historical data
- [ ] **Scheduled evaluations** - Cron-based benchmark runs
- [ ] **Alert system** - Notify on quality degradation
- [ ] **Custom evaluators** - Plugin system for domain-specific criteria

### Long-term
- [ ] **Multi-provider support** - Compare Mistral vs OpenAI vs Anthropic
- [ ] **Fine-tuning integration** - Evaluate fine-tuned models
- [ ] **RAG evaluation** - Retrieval quality metrics
- [ ] **Agent evaluation** - Multi-step task completion

---

## 🧡 Why Mistral?

I chose to build this for Mistral AI specifically because:

### 1. **Technical Excellence**
Mistral's models achieve state-of-the-art performance efficiently. The Mixtral architecture demonstrates innovative thinking in MoE design.

### 2. **European AI Leadership**
As a European company, Mistral represents the opportunity to build world-class AI capabilities in Europe - something I strongly believe in.

### 3. **Open Science Commitment**
Publishing model weights and research openly (Mistral 7B, Mixtral) aligns with my values around AI democratization.

### 4. **Speed of Execution**
From founding to deploying production models in months shows the kind of ambitious, fast-moving environment I thrive in.

### 5. **Strategic Positioning**
Mistral is uniquely positioned: European data sovereignty, enterprise focus, and technical credibility. The evaluation tooling I'm building here addresses real needs I expect customers to have.

> *"I want to contribute to building the infrastructure that makes LLMs reliable in production."*

---

## 🎯 Internship Scope

This project is **intentionally scoped** to demonstrate engineering judgment, not feature count.

### What this project IS:

- ✅ Implementable by a **single engineer** in a reasonable timeframe
- ✅ Reflective of **real internal tooling** used by LLM teams
- ✅ A foundation for deeper work (evaluation pipelines, dashboards, infra)
- ✅ Production-ready architecture that could scale

### What this project is NOT:

- ❌ A research paper or novel algorithm
- ❌ A comprehensive benchmark suite
- ❌ Over-engineered with unnecessary complexity

### Natural evolution path:

If this were internal tooling at Mistral, it could evolve into:

1. **Continuous evaluation pipeline** running on every model release
2. **Regression detection system** alerting on quality drops
3. **Customer-facing evaluation dashboard** for enterprise users
4. **A/B testing framework** for prompt optimization
5. **Integration with training pipelines** for RLHF data collection

> *"The best projects aren't the ones with the most features—they're the ones that solve real problems elegantly."*

---

## 🛠️ Development

### Run tests
```bash
pytest tests/ -v
```

### Format code
```bash
black app/
isort app/
```

### Type check
```bash
mypy app/
```

---

## 📝 License

MIT License - feel free to use this for your own projects!

---

## 👤 Author

**Malek Gatoufi**

Built for the Mistral AI internship application.

---

<div align="center">

**⭐ If you found this useful, star the repo!**

</div>
