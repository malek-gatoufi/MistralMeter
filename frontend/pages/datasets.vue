<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-white">Evaluation Datasets</h2>
        <p class="text-dark-400">Manage and browse your prompt datasets</p>
      </div>
    </div>

    <!-- Datasets List -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="dataset in datasets" 
        :key="dataset.name"
        class="card-hover p-6"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-dark-700 flex items-center justify-center">
              <DocumentTextIcon class="w-5 h-5 text-dark-400" />
            </div>
            <div>
              <h3 class="font-semibold text-white">{{ dataset.name }}</h3>
              <p class="text-sm text-dark-400">{{ dataset.description || 'No description' }}</p>
            </div>
          </div>
          <span class="badge-info">{{ dataset.prompt_count }} prompts</span>
        </div>

        <!-- Categories -->
        <div class="flex flex-wrap gap-2 mb-4">
          <span 
            v-for="cat in dataset.categories" 
            :key="cat"
            class="px-2 py-1 text-xs rounded bg-dark-700 text-dark-300"
          >
            {{ cat }}
          </span>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <button 
            @click="viewDataset(dataset.name)"
            class="btn-secondary flex-1 text-sm"
          >
            <EyeIcon class="w-4 h-4" />
            View
          </button>
          <NuxtLink 
            :to="`/batch?dataset=${dataset.name}`"
            class="btn-primary flex-1 text-sm"
          >
            <PlayIcon class="w-4 h-4" />
            Evaluate
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Dataset Detail Modal -->
    <div 
      v-if="selectedDataset"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-dark-950/80 backdrop-blur-sm"
        @click="selectedDataset = null"
      />
      
      <!-- Modal -->
      <div class="relative w-full max-w-4xl max-h-[80vh] card p-6 overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold text-white">{{ selectedDataset.name }}</h3>
            <p class="text-sm text-dark-400">{{ selectedDataset.description }}</p>
          </div>
          <button 
            @click="selectedDataset = null"
            class="btn-ghost p-2"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Prompts List -->
        <div class="flex-1 overflow-y-auto scrollbar-thin space-y-3">
          <div 
            v-for="(prompt, i) in selectedDataset.prompts" 
            :key="i"
            class="p-4 bg-dark-800/50 rounded-lg"
          >
            <div class="flex items-start gap-3">
              <span class="text-sm font-medium text-dark-500 w-6">{{ i + 1 }}</span>
              <div class="flex-1">
                <p class="text-white">{{ prompt.prompt }}</p>
                <div class="flex items-center gap-3 mt-2">
                  <span class="text-xs px-2 py-0.5 rounded bg-dark-700 text-dark-300">
                    {{ prompt.expected_style || 'educational' }}
                  </span>
                  <span v-if="prompt.category" class="text-xs text-dark-500">
                    {{ prompt.category }}
                  </span>
                </div>
                <p v-if="prompt.reference_answer" class="text-sm text-dark-400 mt-2 italic">
                  Reference: {{ prompt.reference_answer }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-4 pt-4 border-t border-dark-700 flex justify-end gap-3">
          <button @click="selectedDataset = null" class="btn-secondary">
            Close
          </button>
          <NuxtLink 
            :to="`/batch?dataset=${selectedDataset.name}`"
            class="btn-primary"
            @click="selectedDataset = null"
          >
            <PlayIcon class="w-4 h-4" />
            Run Evaluation
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="datasets.length === 0 && !loading" class="card p-12 flex flex-col items-center justify-center text-center">
      <div class="w-16 h-16 rounded-2xl bg-dark-800 flex items-center justify-center mb-4">
        <DocumentTextIcon class="w-8 h-8 text-dark-500" />
      </div>
      <h3 class="text-lg font-semibold text-white">No Datasets Found</h3>
      <p class="text-dark-400 mt-1">Add JSON datasets to the datasets/ folder</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  DocumentTextIcon, 
  EyeIcon, 
  PlayIcon,
  XMarkIcon 
} from '@heroicons/vue/24/outline'
import type { DatasetInfo, Dataset } from '~/composables/useApi'

const { getDatasets, getDataset } = useApi()

const loading = ref(true)
const datasets = ref<DatasetInfo[]>([])
const selectedDataset = ref<Dataset | null>(null)

// Load datasets
onMounted(async () => {
  try {
    datasets.value = await getDatasets()
  } catch (e) {
    console.error('Failed to load datasets:', e)
  } finally {
    loading.value = false
  }
})

// View dataset details
const viewDataset = async (name: string) => {
  try {
    selectedDataset.value = await getDataset(name)
  } catch (e) {
    console.error('Failed to load dataset:', e)
  }
}
</script>
