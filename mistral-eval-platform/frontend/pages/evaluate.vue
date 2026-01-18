<template>
  <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8 animate-in">
    <!-- Input Section -->
    <div class="space-y-6">
      <!-- Templates -->
      <PromptTemplates @select="selectTemplate" />
      
      <!-- History -->
      <EvaluationHistory @select="selectFromHistory" />
      
      <div class="card p-5 sm:p-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="section-title">Prompt Configuration</h3>
          <div class="flex items-center gap-2">
            <span class="text-2xs text-dark-500">Ctrl+Enter to evaluate</span>
            <span class="badge-primary">v2.0</span>
          </div>
        </div>
        
        <div class="space-y-5">
          <!-- Prompt Input -->
          <div class="input-group">
            <label class="input-label">Prompt</label>
            <textarea
              v-model="prompt"
              class="textarea h-32"
              placeholder="Enter your prompt to evaluate..."
            />
          </div>

          <!-- Model & Judge Selection -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="input-group">
              <label class="input-label">Model to Evaluate</label>
              <select v-model="selectedModel" class="select">
                <option v-for="model in models" :key="model.id" :value="model.id">
                  {{ model.name }}
                </option>
              </select>
            </div>
            <div class="input-group">
              <label class="input-label">Judge Model</label>
              <select v-model="judgeModel" class="select">
                <option v-for="model in models" :key="model.id" :value="model.id">
                  {{ model.name }}
                </option>
              </select>
              <p class="text-2xs text-dark-500 mt-1">Different from evaluated model</p>
            </div>
          </div>

          <!-- Style Selection -->
          <div class="input-group">
            <label class="input-label">Expected Style</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="style in styles"
                :key="style.id"
                @click="selectedStyle = style.id"
                class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200"
                :class="selectedStyle === style.id 
                  ? 'bg-mistral-500/20 text-mistral-400 border border-mistral-500/40' 
                  : 'bg-dark-800/60 text-dark-300 border border-dark-700/50 hover:border-dark-600'"
              >
                {{ style.name }}
              </button>
            </div>
          </div>

          <!-- Variance Analysis -->
          <div class="card p-4 bg-dark-800/40 border-dark-700/50">
            <div class="flex items-center justify-between mb-3">
              <div>
                <label class="text-sm font-medium text-white">Variance Analysis</label>
                <p class="text-2xs text-dark-400 mt-0.5">Run multiple times for statistical confidence</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="enableVariance" class="sr-only peer">
                <div class="w-11 h-6 bg-dark-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-mistral-500/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-mistral-500"></div>
              </label>
            </div>
            <div v-if="enableVariance" class="flex items-center gap-4">
              <label class="text-sm text-dark-400">Runs:</label>
              <div class="flex items-center gap-2">
                <button 
                  v-for="n in [3, 5, 7, 10]" 
                  :key="n"
                  @click="runs = n"
                  class="w-10 h-10 rounded-lg text-sm font-medium transition-all"
                  :class="runs === n 
                    ? 'bg-mistral-500 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:bg-dark-600'"
                >
                  {{ n }}
                </button>
              </div>
            </div>
          </div>

          <!-- Cost Calculator -->
          <CostCalculator
            :prompt="prompt"
            :model="selectedModel"
            :max-tokens="maxTokens"
            :runs="enableVariance ? runs : 1"
          />

          <!-- Parameters -->
          <div class="grid grid-cols-2 gap-4">
            <div class="input-group">
              <label class="input-label flex items-center justify-between">
                <span>Temperature</span>
                <span class="text-mistral-400 font-mono">{{ temperature.toFixed(1) }}</span>
              </label>
              <input
                v-model.number="temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                class="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-mistral-500"
              />
            </div>
            <div class="input-group">
              <label class="input-label">Max Tokens</label>
              <input
                v-model.number="maxTokens"
                type="number"
                min="100"
                max="4096"
                class="input"
              />
            </div>
          </div>

          <!-- Reference Answer (Collapsible) -->
          <details class="group">
            <summary class="flex items-center justify-between cursor-pointer text-sm font-medium text-dark-300 hover:text-white transition-colors">
              <span>Reference Answer (Optional)</span>
              <ChevronDownIcon class="w-4 h-4 group-open:rotate-180 transition-transform" />
            </summary>
            <textarea
              v-model="referenceAnswer"
              class="textarea h-20 mt-3"
              placeholder="Provide a reference answer for comparison..."
            />
          </details>
        </div>

        <!-- Submit Button -->
        <button
          @click="runEvaluation"
          :disabled="!prompt.trim() || loading"
          class="btn-primary w-full mt-6"
        >
          <template v-if="loading">
            <div class="spinner" />
            Evaluating{{ enableVariance ? ` (${currentRun}/${runs})` : '' }}...
          </template>
          <template v-else>
            <BeakerIcon class="w-5 h-5" />
            {{ enableVariance ? `Run ${runs}x Evaluation` : 'Run Evaluation' }}
          </template>
        </button>
      </div>
    </div>

    <!-- Results Section -->
    <div class="space-y-6">
      <!-- Loading State -->
      <div v-if="loading" class="card p-8 sm:p-12 flex flex-col items-center justify-center">
        <div class="relative">
          <div class="spinner-lg" />
          <div class="absolute inset-0 spinner-lg opacity-30 scale-150" />
        </div>
        <p class="mt-6 text-white font-medium">Running evaluation...</p>
        <p class="text-sm text-dark-400 mt-1">{{ enableVariance ? `Run ${currentRun} of ${runs}` : 'This may take a few seconds' }}</p>
        
        <!-- Progress bar for variance -->
        <div v-if="enableVariance" class="w-full max-w-xs mt-4">
          <div class="progress-bar">
            <div class="progress-bar-fill" :style="{ width: `${(currentRun / runs) * 100}%` }" />
          </div>
        </div>
      </div>

      <!-- Results -->
      <template v-else-if="result">
        <!-- Quality Score Card -->
        <div class="card p-5 sm:p-6 overflow-hidden relative">
          <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-mistral-500/10 to-transparent rounded-bl-full" />
          
          <div class="relative">
            <div class="flex items-center justify-between mb-5">
              <h3 class="section-title">Quality Score</h3>
              <QualityBadge :score="result.metrics.quality.score" />
            </div>
            
            <div class="flex flex-col sm:flex-row items-center gap-6 sm:gap-8">
              <!-- Score Ring -->
              <div class="flex-shrink-0">
                <ScoreRing :score="result.metrics.quality.score" size="lg" />
              </div>
              
              <!-- Criteria Breakdown -->
              <div class="flex-1 w-full space-y-3">
                <div 
                  v-for="(score, criterion) in result.metrics.quality.criteria_scores" 
                  :key="criterion"
                  class="group"
                >
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-sm text-dark-400 capitalize">{{ criterion.replace('_', ' ') }}</span>
                    <span class="text-sm font-semibold text-white">{{ score.toFixed(1) }}</span>
                  </div>
                  <div class="h-2 bg-dark-700/60 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all duration-700 ease-out"
                      :class="getScoreBarColor(score)"
                      :style="{ width: `${score * 10}%` }"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Feedback -->
            <div class="mt-5 p-4 bg-dark-800/40 rounded-xl border border-dark-700/30">
              <div class="flex items-start gap-3">
                <ChatBubbleLeftRightIcon class="w-5 h-5 text-dark-400 flex-shrink-0 mt-0.5" />
                <p class="text-sm text-dark-300 leading-relaxed">{{ result.metrics.quality.feedback }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div class="metric-card group hover:border-emerald-500/30 transition-colors">
            <ClockIcon class="w-5 h-5 text-dark-500 group-hover:text-emerald-400 transition-colors mb-2" />
            <span class="metric-label">Latency</span>
            <span class="metric-value">{{ result.metrics.latency.total_ms.toFixed(0) }}</span>
            <span class="metric-unit">ms</span>
          </div>
          <div v-if="result.metrics.latency.time_to_first_token_ms" class="metric-card group hover:border-sky-500/30 transition-colors">
            <BoltIcon class="w-5 h-5 text-dark-500 group-hover:text-sky-400 transition-colors mb-2" />
            <span class="metric-label">TTFT</span>
            <span class="metric-value">{{ result.metrics.latency.time_to_first_token_ms.toFixed(0) }}</span>
            <span class="metric-unit">ms</span>
          </div>
          <div class="metric-card group hover:border-violet-500/30 transition-colors">
            <CubeIcon class="w-5 h-5 text-dark-500 group-hover:text-violet-400 transition-colors mb-2" />
            <span class="metric-label">Tokens</span>
            <span class="metric-value">{{ result.metrics.tokens.total_tokens }}</span>
            <span class="metric-unit">total</span>
          </div>
          <div class="metric-card group hover:border-amber-500/30 transition-colors">
            <FireIcon class="w-5 h-5 text-dark-500 group-hover:text-amber-400 transition-colors mb-2" />
            <span class="metric-label">Speed</span>
            <span class="metric-value">{{ result.metrics.latency.tokens_per_second?.toFixed(0) || 'N/A' }}</span>
            <span class="metric-unit">tok/s</span>
          </div>
        </div>

        <!-- Token Breakdown -->
        <div class="card p-5 sm:p-6">
          <h3 class="section-title mb-4">Token Usage</h3>
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-dark-400 flex items-center gap-2">
                  <ArrowDownTrayIcon class="w-4 h-4" />
                  Input
                </span>
                <span class="text-white font-medium">{{ result.metrics.tokens.input_tokens }}</span>
              </div>
              <div class="h-3 bg-dark-700/60 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-sky-500 to-sky-400 rounded-full transition-all duration-700"
                  :style="{ width: `${(result.metrics.tokens.input_tokens / result.metrics.tokens.total_tokens) * 100}%` }"
                />
              </div>
            </div>
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-dark-400 flex items-center gap-2">
                  <ArrowUpTrayIcon class="w-4 h-4" />
                  Output
                </span>
                <span class="text-white font-medium">{{ result.metrics.tokens.output_tokens }}</span>
              </div>
              <div class="h-3 bg-dark-700/60 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-mistral-500 to-mistral-400 rounded-full transition-all duration-700"
                  :style="{ width: `${(result.metrics.tokens.output_tokens / result.metrics.tokens.total_tokens) * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Response -->
        <div class="card p-5 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="section-title">Response</h3>
            <button 
              @click="copyResponse"
              class="btn-icon text-dark-400 hover:text-white"
              title="Copy response"
            >
              <ClipboardDocumentIcon class="w-5 h-5" />
            </button>
          </div>
          <div class="code-block max-h-80 overflow-y-auto scrollbar-thin">
            <pre class="whitespace-pre-wrap text-dark-200 text-sm leading-relaxed">{{ result.response }}</pre>
          </div>
        </div>

        <!-- Variance Chart (if multiple runs) -->
        <VarianceChart
          v-if="result.variance_metrics && enableVariance"
          :stats="result.variance_metrics"
          :scores="result.scores"
        />
      </template>

      <!-- Empty State -->
      <div v-else class="card p-8 sm:p-12 flex flex-col items-center justify-center text-center">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-dark-800 to-dark-900 flex items-center justify-center mb-4 border border-dark-700/50">
          <BeakerIcon class="w-8 h-8 text-dark-500" />
        </div>
        <h3 class="text-lg font-semibold text-white">No Results Yet</h3>
        <p class="text-dark-400 mt-1 max-w-xs">Enter a prompt and run an evaluation to see quality metrics, latency, and token usage</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  BeakerIcon, 
  ChevronDownIcon,
  ClockIcon,
  BoltIcon,
  CubeIcon,
  FireIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  ClipboardDocumentIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/vue/24/outline'
import type { EvalResult } from '~/composables/useApi'

const { evaluate, getModels, getStyles } = useApi()

// Form state
const prompt = ref('')
const selectedModel = ref('mistral-small-latest')
const judgeModel = ref('mistral-large-latest')
const selectedStyle = ref('educational')
const temperature = ref(0.7)
const maxTokens = ref(1024)
const referenceAnswer = ref('')
const enableVariance = ref(false)
const runs = ref(5)
const currentRun = ref(0)

// Options
const models = ref<{ id: string; name: string; description: string }[]>([])
const styles = ref<{ id: string; name: string }[]>([])

// Results
const loading = ref(false)
const result = ref<EvalResult | null>(null)
const error = ref<string | null>(null)

// Composables
const { success, error: showError } = useToast()
const { addToHistory } = useLocalStorage()

// Keyboard shortcuts
useKeyboardShortcuts([
  {
    key: 'Enter',
    ctrl: true,
    callback: () => runEvaluation(),
    description: 'Run evaluation'
  },
  {
    key: 'k',
    ctrl: true,
    callback: () => { prompt.value = '' },
    description: 'Clear prompt'
  }
])

// Load options on mount
onMounted(async () => {
  try {
    const [modelsData, stylesData] = await Promise.all([
      getModels(),
      getStyles()
    ])
    models.value = modelsData.models
    styles.value = stylesData.styles
  } catch (e) {
    console.error('Failed to load options:', e)
  }
})

// Run evaluation
const runEvaluation = async () => {
  if (!prompt.value.trim()) return

  loading.value = true
  error.value = null
  result.value = null
  currentRun.value = 1

  try {
    result.value = await evaluate({
      prompt: {
        prompt: prompt.value,
        expected_style: selectedStyle.value,
        reference_answer: referenceAnswer.value || undefined,
      },
      model: selectedModel.value,
      judge_model: judgeModel.value,
      temperature: temperature.value,
      max_tokens: maxTokens.value,
      runs: enableVariance.value ? runs.value : 1,
    })
    
    // Add to history
    addToHistory({
      prompt: prompt.value,
      model: selectedModel.value,
      score: result.value.metrics.quality.overall_score,
      temperature: temperature.value
    })
    
    success('Evaluation completed successfully!')
  } catch (e: any) {
    error.value = e.message
    showError('Evaluation failed: ' + e.message)
    console.error('Evaluation failed:', e)
  } finally {
    loading.value = false
  }
}

// Copy response to clipboard
const copyResponse = async () => {
  if (result.value?.response) {
    await navigator.clipboard.writeText(result.value.response)
    success('Response copied to clipboard!')
  }
}

// Select template
const selectTemplate = (templatePrompt: string) => {
  prompt.value = templatePrompt
  success('Template loaded!')
}

// Select from history
const selectFromHistory = (item: any) => {
  prompt.value = item.prompt
  selectedModel.value = item.model
  if (item.temperature) temperature.value = item.temperature
  success('Loaded from history!')
}

// Helpers
const getScoreBarColor = (score: number) => {
  if (score >= 8) return 'bg-gradient-to-r from-emerald-500 to-emerald-400'
  if (score >= 6) return 'bg-gradient-to-r from-amber-500 to-amber-400'
  return 'bg-gradient-to-r from-rose-500 to-rose-400'
}

// SEO
useSeoMeta({
  title: 'Evaluate',
  description: 'Test prompts with comprehensive quality metrics, latency analysis, and variance tracking.',
})
</script>
