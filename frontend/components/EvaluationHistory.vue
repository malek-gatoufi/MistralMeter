<template>
  <div class="card p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">Recent Evaluations</h3>
      <div class="flex items-center gap-2">
        <button
          v-if="history.length > 0"
          @click="exportHistory"
          class="text-sm text-sky-400 hover:text-sky-300 transition-colors"
        >
          Export
        </button>
        <button
          v-if="history.length > 0"
          @click="confirmClear"
          class="text-sm text-rose-400 hover:text-rose-300 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <div v-if="history.length === 0" class="text-center py-12">
      <ClockIcon class="w-12 h-12 text-dark-600 mx-auto mb-3" />
      <p class="text-dark-400">No evaluations yet</p>
      <p class="text-sm text-dark-500 mt-1">Your recent prompts will appear here</p>
    </div>

    <div v-else class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="item in history.slice(0, 20)"
        :key="item.id"
        @click="$emit('select', item)"
        class="group cursor-pointer p-4 rounded-lg border border-dark-700/50 hover:border-mistral-500/40 hover:bg-dark-800/40 transition-all duration-200"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white line-clamp-2 mb-2">{{ item.prompt }}</p>
            <div class="flex flex-wrap items-center gap-2 text-xs text-dark-400">
              <span class="inline-flex items-center gap-1">
                <CpuChipIcon class="w-3.5 h-3.5" />
                {{ item.model }}
              </span>
              <span>•</span>
              <span>{{ formatDate(item.timestamp) }}</span>
              <span v-if="item.score" class="inline-flex items-center gap-1 text-mistral-400">
                •
                <span class="font-semibold">{{ item.score.toFixed(1) }}</span>
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <button
              @click.stop="toggleFavorite(item.prompt)"
              class="p-1 rounded hover:bg-dark-700/50 transition-colors"
            >
              <component
                :is="isFavorite(item.prompt) ? StarIconSolid : StarIcon"
                class="w-4 h-4"
                :class="isFavorite(item.prompt) ? 'text-yellow-400' : 'text-dark-500'"
              />
            </button>
            <button
              @click.stop="removeFromHistory(item.id)"
              class="p-1 rounded hover:bg-dark-700/50 transition-colors opacity-0 group-hover:opacity-100"
            >
              <XMarkIcon class="w-4 h-4 text-dark-500 hover:text-rose-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ClockIcon, CpuChipIcon, StarIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { useLocalStorage } from '~/composables/useLocalStorage'
import { useToast } from '~/composables/useToast'

const emit = defineEmits<{
  select: [item: any]
}>()

const { history, removeFromHistory, clearHistory, toggleFavorite, isFavorite } = useLocalStorage()
const { success, warning } = useToast()

const formatDate = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

const confirmClear = () => {
  if (confirm('Are you sure you want to clear all history?')) {
    clearHistory()
    success('History cleared')
  }
}

const exportHistory = () => {
  const dataStr = JSON.stringify(history.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `mistral-eval-history-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
  success('History exported')
}
</script>
