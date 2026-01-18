<template>
  <div class="card p-4 bg-dark-800/40 border-dark-700/50">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <CurrencyDollarIcon class="w-5 h-5 text-emerald-400" />
        <h4 class="text-sm font-semibold text-white">Cost Estimate</h4>
      </div>
      <button
        @click="showDetails = !showDetails"
        class="text-xs text-mistral-400 hover:text-mistral-300 transition-colors"
      >
        {{ showDetails ? 'Hide' : 'Details' }}
      </button>
    </div>

    <div class="space-y-3">
      <!-- Total Cost -->
      <div class="flex items-baseline gap-2">
        <span class="text-3xl font-bold text-emerald-400">
          ${{ totalCost.toFixed(6) }}
        </span>
        <span class="text-sm text-dark-400">per run</span>
      </div>

      <!-- Breakdown (if details shown) -->
      <div v-if="showDetails" class="space-y-2 pt-3 border-t border-dark-700/50">
        <div class="flex justify-between text-sm">
          <span class="text-dark-400">Input tokens:</span>
          <span class="text-white font-mono">{{ estimatedInputTokens }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-dark-400">Output tokens:</span>
          <span class="text-white font-mono">{{ maxTokens }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-dark-400">Input cost:</span>
          <span class="text-emerald-400 font-mono">${{ inputCost.toFixed(6) }}</span>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-dark-400">Output cost:</span>
          <span class="text-emerald-400 font-mono">${{ outputCost.toFixed(6) }}</span>
        </div>
        
        <!-- Multiple runs -->
        <div v-if="runs > 1" class="pt-2 border-t border-dark-700/30">
          <div class="flex justify-between text-sm font-semibold">
            <span class="text-white">Total ({{ runs }} runs):</span>
            <span class="text-emerald-400 font-mono">${{ (totalCost * runs).toFixed(6) }}</span>
          </div>
        </div>
      </div>

      <!-- Model pricing info -->
      <div class="text-2xs text-dark-500 pt-2 border-t border-dark-700/30">
        <p>{{ modelPricing[model]?.name || 'Unknown model' }}</p>
        <p class="mt-1">
          Input: ${{ modelPricing[model]?.input || 0 }}/1K • 
          Output: ${{ modelPricing[model]?.output || 0 }}/1K
        </p>
      </div>

      <!-- Warning for high costs -->
      <div v-if="totalCost * runs > 0.01" class="flex items-start gap-2 p-2 rounded bg-yellow-500/10 border border-yellow-500/20">
        <ExclamationTriangleIcon class="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
        <p class="text-2xs text-yellow-400">
          High token usage detected. Consider reducing max_tokens or runs.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { CurrencyDollarIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

interface Props {
  prompt: string
  model: string
  maxTokens: number
  runs?: number
}

const props = withDefaults(defineProps<Props>(), {
  runs: 1
})

const showDetails = ref(false)

// Mistral pricing (approximate, per 1K tokens)
const modelPricing: Record<string, { name: string; input: number; output: number }> = {
  'mistral-small-latest': { name: 'Mistral Small', input: 0.002, output: 0.006 },
  'mistral-medium-latest': { name: 'Mistral Medium', input: 0.0027, output: 0.0081 },
  'mistral-large-latest': { name: 'Mistral Large', input: 0.004, output: 0.012 },
  'open-mistral-7b': { name: 'Open Mistral 7B', input: 0.00025, output: 0.00025 },
  'open-mixtral-8x7b': { name: 'Open Mixtral 8x7B', input: 0.0007, output: 0.0007 },
  'open-mixtral-8x22b': { name: 'Open Mixtral 8x22B', input: 0.002, output: 0.006 }
}

// Estimate input tokens (rough: 1 token ≈ 0.75 words)
const estimatedInputTokens = computed(() => {
  const words = props.prompt.trim().split(/\s+/).length
  return Math.ceil(words * 1.3) // 1 word ≈ 1.3 tokens on average
})

const inputCost = computed(() => {
  const pricing = modelPricing[props.model]
  if (!pricing) return 0
  return (estimatedInputTokens.value / 1000) * pricing.input
})

const outputCost = computed(() => {
  const pricing = modelPricing[props.model]
  if (!pricing) return 0
  return (props.maxTokens / 1000) * pricing.output
})

const totalCost = computed(() => {
  return inputCost.value + outputCost.value
})
</script>
