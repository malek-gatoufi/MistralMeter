<template>
  <div class="space-y-6">
    <!-- Configuration -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold text-white mb-4">Compare Models</h3>
      
      <div class="space-y-4">
        <!-- Prompt -->
        <div>
          <label class="block text-sm font-medium text-dark-300 mb-2">Prompt</label>
          <textarea
            v-model="prompt"
            class="textarea h-24"
            placeholder="Enter a prompt to compare models..."
          />
        </div>

        <!-- Model Selection -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              <span class="inline-flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-blue-500" />
                Model A
              </span>
            </label>
            <select v-model="modelA" class="select">
              <option v-for="model in models" :key="model.id" :value="model.id">
                {{ model.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              <span class="inline-flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-mistral-500" />
                Model B
              </span>
            </label>
            <select v-model="modelB" class="select">
              <option v-for="model in models" :key="model.id" :value="model.id">
                {{ model.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Parameters -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              Temperature: {{ temperature }}
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
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">Max Tokens</label>
            <input
              v-model.number="maxTokens"
              type="number"
              min="100"
              max="4096"
              class="input"
            />
          </div>
        </div>

        <!-- Compare Button -->
        <button
          @click="runComparison"
          :disabled="!prompt.trim() || loading || modelA === modelB"
          class="btn-primary w-full"
        >
          <template v-if="loading">
            <div class="spinner" />
            Comparing...
          </template>
          <template v-else>
            <ScaleIcon class="w-5 h-5" />
            Compare Models
          </template>
        </button>
        
        <p v-if="modelA === modelB" class="text-sm text-yellow-400 text-center">
          Please select different models to compare
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card p-12 flex flex-col items-center justify-center">
      <div class="spinner w-12 h-12 border-4" />
      <p class="mt-4 text-dark-300">Running comparison...</p>
      <p class="text-sm text-dark-500">Evaluating both models in parallel</p>
    </div>

    <!-- Results -->
    <template v-else-if="result">
      <!-- Winner Banner -->
      <div 
        class="card p-6"
        :class="[
          result.winner === modelA ? 'border-blue-500/50 bg-blue-500/5' : 
          result.winner === modelB ? 'border-mistral-500/50 bg-mistral-500/5' : 
          'border-dark-600'
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div 
              class="w-12 h-12 rounded-xl flex items-center justify-center"
              :class="[
                result.winner === modelA ? 'bg-blue-500/20' : 
                result.winner === modelB ? 'bg-mistral-500/20' : 
                'bg-dark-700'
              ]"
            >
              <TrophyIcon 
                class="w-6 h-6"
                :class="[
                  result.winner === modelA ? 'text-blue-400' : 
                  result.winner === modelB ? 'text-mistral-400' : 
                  'text-dark-400'
                ]"
              />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">
                {{ result.winner ? `Winner: ${result.winner}` : 'Tie' }}
              </h3>
              <p class="text-sm text-dark-400">{{ result.comparison_summary }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Side by Side Comparison -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Model A -->
        <div class="space-y-4">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-blue-500" />
            <h3 class="font-semibold text-white">{{ modelA }}</h3>
            <span v-if="result.winner === modelA" class="badge-success">Winner</span>
          </div>

          <!-- Metrics -->
          <div class="grid grid-cols-2 gap-3">
            <div class="metric-card">
              <span class="metric-label">Quality</span>
              <span class="metric-value text-xl">{{ result.model_a.metrics.quality.score.toFixed(1) }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Latency</span>
              <span class="metric-value text-xl">{{ result.model_a.metrics.latency.total_ms.toFixed(0) }}ms</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Tokens</span>
              <span class="metric-value text-xl">{{ result.model_a.metrics.tokens.output_tokens }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Speed</span>
              <span class="metric-value text-xl">{{ result.model_a.metrics.latency.tokens_per_second?.toFixed(0) || 'N/A' }}</span>
            </div>
          </div>

          <!-- Response -->
          <div class="card p-4">
            <h4 class="text-sm font-medium text-dark-400 mb-2">Response</h4>
            <div class="code-block max-h-64 overflow-y-auto scrollbar-thin">
              <pre class="whitespace-pre-wrap text-sm text-dark-200">{{ result.model_a.response }}</pre>
            </div>
          </div>

          <!-- Quality Feedback -->
          <div class="card p-4 bg-blue-500/5 border-blue-500/20">
            <h4 class="text-sm font-medium text-blue-400 mb-2">Quality Feedback</h4>
            <p class="text-sm text-dark-300">{{ result.model_a.metrics.quality.feedback }}</p>
          </div>
        </div>

        <!-- Model B -->
        <div class="space-y-4">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-mistral-500" />
            <h3 class="font-semibold text-white">{{ modelB }}</h3>
            <span v-if="result.winner === modelB" class="badge-success">Winner</span>
          </div>

          <!-- Metrics -->
          <div class="grid grid-cols-2 gap-3">
            <div class="metric-card">
              <span class="metric-label">Quality</span>
              <span class="metric-value text-xl">{{ result.model_b.metrics.quality.score.toFixed(1) }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Latency</span>
              <span class="metric-value text-xl">{{ result.model_b.metrics.latency.total_ms.toFixed(0) }}ms</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Tokens</span>
              <span class="metric-value text-xl">{{ result.model_b.metrics.tokens.output_tokens }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Speed</span>
              <span class="metric-value text-xl">{{ result.model_b.metrics.latency.tokens_per_second?.toFixed(0) || 'N/A' }}</span>
            </div>
          </div>

          <!-- Response -->
          <div class="card p-4">
            <h4 class="text-sm font-medium text-dark-400 mb-2">Response</h4>
            <div class="code-block max-h-64 overflow-y-auto scrollbar-thin">
              <pre class="whitespace-pre-wrap text-sm text-dark-200">{{ result.model_b.response }}</pre>
            </div>
          </div>

          <!-- Quality Feedback -->
          <div class="card p-4 bg-mistral-500/5 border-mistral-500/20">
            <h4 class="text-sm font-medium text-mistral-400 mb-2">Quality Feedback</h4>
            <p class="text-sm text-dark-300">{{ result.model_b.metrics.quality.feedback }}</p>
          </div>
        </div>
      </div>

      <!-- Comparison Chart -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Metrics Comparison</h3>
        <div class="space-y-4">
          <!-- Quality -->
          <ComparisonBar 
            label="Quality Score"
            :value-a="result.model_a.metrics.quality.score"
            :value-b="result.model_b.metrics.quality.score"
            :max="10"
            unit=""
            higher-better
          />
          <!-- Latency -->
          <ComparisonBar 
            label="Latency"
            :value-a="result.model_a.metrics.latency.total_ms"
            :value-b="result.model_b.metrics.latency.total_ms"
            :max="Math.max(result.model_a.metrics.latency.total_ms, result.model_b.metrics.latency.total_ms) * 1.2"
            unit="ms"
            :higher-better="false"
          />
          <!-- Output Tokens -->
          <ComparisonBar 
            label="Output Tokens"
            :value-a="result.model_a.metrics.tokens.output_tokens"
            :value-b="result.model_b.metrics.tokens.output_tokens"
            :max="Math.max(result.model_a.metrics.tokens.output_tokens, result.model_b.metrics.tokens.output_tokens) * 1.2"
            unit=""
          />
        </div>
      </div>
    </template>

    <!-- Empty State -->
    <div v-else class="card p-12 flex flex-col items-center justify-center text-center">
      <div class="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mb-4">
        <ScaleIcon class="w-8 h-8 text-dark-500" />
      </div>
      <h3 class="text-lg font-semibold text-white">Compare Models</h3>
      <p class="text-dark-400 mt-1">Select two models and enter a prompt to compare their performance</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ScaleIcon, TrophyIcon } from '@heroicons/vue/24/outline'
import type { CompareResult } from '~/composables/useApi'

const { compare, getModels } = useApi()

// Form state
const prompt = ref('')
const modelA = ref('mistral-small-latest')
const modelB = ref('mistral-large-latest')
const temperature = ref(0.7)
const maxTokens = ref(1024)

// Options
const models = ref<{ id: string; name: string; description: string }[]>([])

// Results
const loading = ref(false)
const result = ref<CompareResult | null>(null)

// Load models
onMounted(async () => {
  try {
    const data = await getModels()
    models.value = data.models
  } catch (e) {
    console.error('Failed to load models:', e)
  }
})

// Run comparison
const runComparison = async () => {
  if (!prompt.value.trim() || modelA.value === modelB.value) return

  loading.value = true
  result.value = null

  try {
    result.value = await compare(
      { prompt: prompt.value },
      modelA.value,
      modelB.value,
      temperature.value,
      maxTokens.value
    )
  } catch (e) {
    console.error('Comparison failed:', e)
  } finally {
    loading.value = false
  }
}
</script>
