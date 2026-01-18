<template>
  <div class="space-y-6">
    <!-- Configuration -->
    <div class="card p-6">
      <h3 class="text-lg font-semibold text-white mb-4">Batch Evaluation</h3>
      
      <div class="space-y-4">
        <!-- Dataset Selection -->
        <div>
          <label class="block text-sm font-medium text-dark-300 mb-2">Select Dataset</label>
          <select v-model="selectedDataset" class="select">
            <option value="">-- Select a dataset --</option>
            <option v-for="ds in datasets" :key="ds.name" :value="ds.name">
              {{ ds.name }} ({{ ds.prompt_count }} prompts)
            </option>
          </select>
        </div>

        <!-- Model Selection -->
        <div>
          <label class="block text-sm font-medium text-dark-300 mb-2">Model</label>
          <select v-model="selectedModel" class="select">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
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

        <!-- Run Button -->
        <button
          @click="runBatchEval"
          :disabled="!selectedDataset || loading"
          class="btn-primary w-full"
        >
          <template v-if="loading">
            <div class="spinner" />
            Evaluating {{ currentProgress }} / {{ totalPrompts }}...
          </template>
          <template v-else>
            <ChartBarIcon class="w-5 h-5" />
            Run Batch Evaluation
          </template>
        </button>
      </div>
    </div>

    <!-- Loading Progress -->
    <div v-if="loading" class="card p-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-dark-300">Progress</span>
        <span class="text-sm text-dark-400">{{ currentProgress }} / {{ totalPrompts }}</span>
      </div>
      <div class="h-2 bg-dark-700 rounded-full overflow-hidden">
        <div 
          class="h-full bg-mistral-500 rounded-full transition-all duration-300"
          :style="{ width: `${(currentProgress / totalPrompts) * 100}%` }"
        />
      </div>
    </div>

    <!-- Results -->
    <template v-else-if="result">
      <!-- Summary Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div class="metric-card">
          <span class="metric-label">Prompts</span>
          <span class="metric-value">{{ result.summary.count }}</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Avg Quality</span>
          <span class="metric-value">{{ result.summary.quality.avg_score.toFixed(1) }}</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Avg Latency</span>
          <span class="metric-value">{{ result.summary.latency.avg_ms.toFixed(0) }}</span>
          <span class="metric-unit">ms</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">P50 Latency</span>
          <span class="metric-value">{{ result.summary.latency.p50_ms.toFixed(0) }}</span>
          <span class="metric-unit">ms</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Total Tokens</span>
          <span class="metric-value">{{ result.summary.tokens.total.toLocaleString() }}</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Est. Cost</span>
          <span class="metric-value">${{ result.summary.estimated_cost_usd.toFixed(4) }}</span>
        </div>
      </div>

      <!-- Quality Distribution -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Quality Distribution</h3>
        <div class="h-64 flex items-end gap-2">
          <div 
            v-for="(r, i) in result.results" 
            :key="i"
            class="flex-1 flex flex-col items-center gap-2"
          >
            <div 
              class="w-full rounded-t transition-all duration-300 hover:opacity-80 cursor-pointer"
              :class="getScoreColor(r.metrics.quality.score)"
              :style="{ height: `${(r.metrics.quality.score / 10) * 100}%` }"
              :title="`Prompt ${i + 1}: ${r.metrics.quality.score.toFixed(1)}`"
            />
            <span class="text-xs text-dark-500">{{ i + 1 }}</span>
          </div>
        </div>
        <div class="flex justify-between mt-4 text-sm text-dark-400">
          <span>Min: {{ result.summary.quality.min_score.toFixed(1) }}</span>
          <span>Avg: {{ result.summary.quality.avg_score.toFixed(1) }}</span>
          <span>Max: {{ result.summary.quality.max_score.toFixed(1) }}</span>
        </div>
      </div>

      <!-- Individual Results -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Individual Results</h3>
        <div class="space-y-3 max-h-96 overflow-y-auto scrollbar-thin">
          <div 
            v-for="(r, i) in result.results" 
            :key="i"
            class="p-4 bg-dark-800/50 rounded-lg hover:bg-dark-800 transition-colors cursor-pointer"
            @click="expandedResult = expandedResult === i ? null : i"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <span class="text-sm font-medium text-dark-400 w-8">#{{ i + 1 }}</span>
                <p class="text-white truncate">{{ r.prompt }}</p>
              </div>
              <div class="flex items-center gap-4 flex-shrink-0">
                <QualityBadge :score="r.metrics.quality.score" size="sm" />
                <span class="text-sm text-dark-400">{{ r.metrics.latency.total_ms.toFixed(0) }}ms</span>
                <ChevronDownIcon 
                  class="w-5 h-5 text-dark-400 transition-transform"
                  :class="{ 'rotate-180': expandedResult === i }"
                />
              </div>
            </div>
            
            <!-- Expanded Details -->
            <div v-if="expandedResult === i" class="mt-4 pt-4 border-t border-dark-700 space-y-3">
              <div class="grid grid-cols-4 gap-3">
                <div class="text-center">
                  <p class="text-xs text-dark-400">Quality</p>
                  <p class="text-lg font-semibold text-white">{{ r.metrics.quality.score.toFixed(1) }}</p>
                </div>
                <div class="text-center">
                  <p class="text-xs text-dark-400">Latency</p>
                  <p class="text-lg font-semibold text-white">{{ r.metrics.latency.total_ms.toFixed(0) }}ms</p>
                </div>
                <div class="text-center">
                  <p class="text-xs text-dark-400">Tokens</p>
                  <p class="text-lg font-semibold text-white">{{ r.metrics.tokens.output_tokens }}</p>
                </div>
                <div class="text-center">
                  <p class="text-xs text-dark-400">Speed</p>
                  <p class="text-lg font-semibold text-white">{{ r.metrics.latency.tokens_per_second?.toFixed(0) || 'N/A' }}</p>
                </div>
              </div>
              <div class="p-3 bg-dark-900 rounded-lg">
                <p class="text-sm text-dark-300">{{ r.metrics.quality.feedback }}</p>
              </div>
              <div class="code-block max-h-48 overflow-y-auto">
                <pre class="text-sm text-dark-200 whitespace-pre-wrap">{{ r.response }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Empty State -->
    <div v-else class="card p-12 flex flex-col items-center justify-center text-center">
      <div class="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mb-4">
        <ChartBarIcon class="w-8 h-8 text-dark-500" />
      </div>
      <h3 class="text-lg font-semibold text-white">Batch Evaluation</h3>
      <p class="text-dark-400 mt-1">Select a dataset to run batch evaluation with aggregated metrics</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChartBarIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import type { BatchEvalResult, DatasetInfo } from '~/composables/useApi'

const route = useRoute()
const { evaluateDataset, getDatasets, getModels, getDataset } = useApi()

// Form state
const selectedDataset = ref(route.query.dataset as string || '')
const selectedModel = ref('mistral-small-latest')
const temperature = ref(0.7)
const maxTokens = ref(1024)

// Options
const datasets = ref<DatasetInfo[]>([])
const models = ref<{ id: string; name: string; description: string }[]>([])

// Results
const loading = ref(false)
const result = ref<BatchEvalResult | null>(null)
const expandedResult = ref<number | null>(null)

// Progress tracking
const currentProgress = ref(0)
const totalPrompts = ref(0)

// Load options
onMounted(async () => {
  try {
    const [datasetsData, modelsData] = await Promise.all([
      getDatasets(),
      getModels()
    ])
    datasets.value = datasetsData
    models.value = modelsData.models
  } catch (e) {
    console.error('Failed to load options:', e)
  }
})

// Update total prompts when dataset changes
watch(selectedDataset, async (name) => {
  if (name) {
    const ds = datasets.value.find(d => d.name === name)
    totalPrompts.value = ds?.prompt_count || 0
  }
})

// Run batch evaluation
const runBatchEval = async () => {
  if (!selectedDataset.value) return

  loading.value = true
  result.value = null
  currentProgress.value = 0

  // Simulate progress (actual API doesn't stream progress)
  const progressInterval = setInterval(() => {
    if (currentProgress.value < totalPrompts.value - 1) {
      currentProgress.value++
    }
  }, 500)

  try {
    result.value = await evaluateDataset(
      selectedDataset.value,
      selectedModel.value,
      temperature.value,
      maxTokens.value
    )
    currentProgress.value = totalPrompts.value
  } catch (e) {
    console.error('Batch evaluation failed:', e)
  } finally {
    clearInterval(progressInterval)
    loading.value = false
  }
}

// Helpers
const getScoreColor = (score: number) => {
  if (score >= 8) return 'bg-green-500'
  if (score >= 6) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>
