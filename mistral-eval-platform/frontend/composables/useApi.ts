/**
 * API Composable for MistralMeter
 * Handles all communication with the FastAPI backend
 */

export interface EvalPrompt {
  prompt: string
  expected_style?: string
  reference_answer?: string
  category?: string
}

export interface EvalRequest {
  prompt: EvalPrompt
  model: string
  temperature: number
  max_tokens: number
}

export interface TokenMetrics {
  input_tokens: number
  output_tokens: number
  total_tokens: number
}

export interface LatencyMetrics {
  total_ms: number
  time_to_first_token_ms?: number
  tokens_per_second?: number
}

export interface QualityScore {
  score: number
  feedback: string
  criteria_scores: Record<string, number>
}

export interface EvalMetrics {
  tokens: TokenMetrics
  latency: LatencyMetrics
  quality: QualityScore
}

export interface EvalResult {
  prompt: string
  model: string
  response: string
  metrics: EvalMetrics
}

export interface BatchEvalResult {
  results: EvalResult[]
  summary: {
    count: number
    latency: {
      avg_ms: number
      min_ms: number
      max_ms: number
      p50_ms: number
    }
    tokens: {
      total_input: number
      total_output: number
      total: number
      avg_output_per_prompt: number
    }
    quality: {
      avg_score: number
      min_score: number
      max_score: number
    }
    throughput: {
      tokens_per_second: number
    }
    estimated_cost_usd: number
  }
}

export interface CompareResult {
  prompt: string
  model_a: EvalResult
  model_b: EvalResult
  winner?: string
  comparison_summary: string
}

export interface DatasetInfo {
  name: string
  description?: string
  prompt_count: number
  categories: string[]
}

export interface Dataset {
  name: string
  description?: string
  prompts: EvalPrompt[]
}

export interface ModelInfo {
  id: string
  name: string
  description: string
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBase

  // Generic fetch wrapper
  const apiFetch = async <T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  }

  // Health check
  const checkHealth = () => apiFetch<{ status: string; api_configured: boolean }>('/')

  // Get available models
  const getModels = () => apiFetch<{ models: ModelInfo[] }>('/models')

  // Get available styles
  const getStyles = () => apiFetch<{ styles: { id: string; name: string }[] }>('/styles')

  // Single evaluation
  const evaluate = (request: EvalRequest) => 
    apiFetch<EvalResult>('/evaluate', {
      method: 'POST',
      body: JSON.stringify(request),
    })

  // Batch evaluation
  const evaluateBatch = (prompts: EvalPrompt[], model: string, temperature: number, max_tokens: number) =>
    apiFetch<BatchEvalResult>('/evaluate/batch', {
      method: 'POST',
      body: JSON.stringify({ prompts, model, temperature, max_tokens }),
    })

  // Model comparison
  const compare = (prompt: EvalPrompt, model_a: string, model_b: string, temperature: number, max_tokens: number) =>
    apiFetch<CompareResult>('/compare', {
      method: 'POST',
      body: JSON.stringify({ prompt, model_a, model_b, temperature, max_tokens }),
    })

  // List datasets
  const getDatasets = () => apiFetch<DatasetInfo[]>('/datasets')

  // Get single dataset
  const getDataset = (name: string) => apiFetch<Dataset>(`/datasets/${name}`)

  // Evaluate dataset
  const evaluateDataset = (name: string, model: string, temperature: number = 0.7, max_tokens: number = 1024) =>
    apiFetch<BatchEvalResult>(`/datasets/${name}/evaluate?model=${model}&temperature=${temperature}&max_tokens=${max_tokens}`, {
      method: 'POST',
    })

  // Stream response
  const streamEvaluate = async function* (request: EvalRequest): AsyncGenerator<string> {
    const response = await fetch(`${baseUrl}/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const text = decoder.decode(value)
      const lines = text.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') return
          try {
            const parsed = JSON.parse(data)
            if (parsed.token) yield parsed.token
          } catch {}
        }
      }
    }
  }

  return {
    checkHealth,
    getModels,
    getStyles,
    evaluate,
    evaluateBatch,
    compare,
    getDatasets,
    getDataset,
    evaluateDataset,
    streamEvaluate,
  }
}
