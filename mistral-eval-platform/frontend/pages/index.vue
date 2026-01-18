<template>
  <div class="space-y-6 lg:space-y-8 animate-in">
    <!-- Hero Section with Gradient -->
    <section class="relative overflow-hidden rounded-2xl lg:rounded-3xl bg-gradient-to-br from-dark-900 via-dark-900 to-mistral-950/30 border border-dark-700/50 p-6 sm:p-8 lg:p-10">
      <!-- Background decoration -->
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-mistral-500/10 via-transparent to-transparent" />
      <div class="absolute top-0 right-0 w-64 h-64 bg-mistral-500/5 rounded-full blur-3xl" />
      
      <div class="relative">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div class="max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-mistral-500/10 border border-mistral-500/20 mb-4">
              <span class="w-2 h-2 rounded-full bg-mistral-500 animate-pulse" />
              <span class="text-xs font-medium text-mistral-400">Production-Ready Evaluation</span>
            </div>
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-white text-balance">
              Evaluate LLMs with
              <span class="gradient-text">Confidence</span>
            </h1>
            <p class="mt-4 text-base sm:text-lg text-dark-300 text-pretty max-w-xl">
              Measure latency, quality, and variance. Compare models. Make data-driven decisions.
            </p>
          </div>
          
          <!-- Quick Stats -->
          <div class="grid grid-cols-2 gap-3 lg:gap-4">
            <div class="card p-4 text-center">
              <div class="text-2xl sm:text-3xl font-bold text-white">{{ models.length }}</div>
              <div class="text-xs text-dark-400 mt-1">Models</div>
            </div>
            <div class="card p-4 text-center">
              <div class="text-2xl sm:text-3xl font-bold text-white">{{ datasets.length }}</div>
              <div class="text-xs text-dark-400 mt-1">Datasets</div>
            </div>
            <div class="card p-4 text-center">
              <div class="text-2xl sm:text-3xl font-bold text-white">{{ totalPrompts }}</div>
              <div class="text-xs text-dark-400 mt-1">Prompts</div>
            </div>
            <div class="card p-4 text-center">
              <div class="flex items-center justify-center gap-1.5">
                <div 
                  class="w-2.5 h-2.5 rounded-full"
                  :class="apiConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"
                />
                <span class="text-lg font-bold" :class="apiConnected ? 'text-emerald-400' : 'text-rose-400'">
                  {{ apiConnected ? 'Live' : 'Off' }}
                </span>
              </div>
              <div class="text-xs text-dark-400 mt-1">API Status</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Actions -->
    <section>
      <h2 class="section-title mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <NuxtLink to="/evaluate" class="group">
          <div class="card-hover p-5 sm:p-6 h-full">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-mistral-500/20 to-mistral-600/10 flex items-center justify-center group-hover:from-mistral-500/30 group-hover:to-mistral-600/20 transition-all duration-300 flex-shrink-0">
                <BeakerIcon class="w-6 h-6 text-mistral-400" />
              </div>
              <div class="min-w-0">
                <h3 class="font-semibold text-white group-hover:text-mistral-400 transition-colors">Single Evaluation</h3>
                <p class="text-sm text-dark-400 mt-1">Test prompts with variance analysis</p>
              </div>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink to="/compare" class="group">
          <div class="card-hover p-5 sm:p-6 h-full">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500/20 to-sky-600/10 flex items-center justify-center group-hover:from-sky-500/30 group-hover:to-sky-600/20 transition-all duration-300 flex-shrink-0">
                <ScaleIcon class="w-6 h-6 text-sky-400" />
              </div>
              <div class="min-w-0">
                <h3 class="font-semibold text-white group-hover:text-sky-400 transition-colors">Compare Models</h3>
                <p class="text-sm text-dark-400 mt-1">Side-by-side A/B testing</p>
              </div>
            </div>
          </div>
        </NuxtLink>

        <NuxtLink to="/batch" class="group sm:col-span-2 lg:col-span-1">
          <div class="card-hover p-5 sm:p-6 h-full">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500/20 to-violet-600/10 flex items-center justify-center group-hover:from-violet-500/30 group-hover:to-violet-600/20 transition-all duration-300 flex-shrink-0">
                <ChartBarIcon class="w-6 h-6 text-violet-400" />
              </div>
              <div class="min-w-0">
                <h3 class="font-semibold text-white group-hover:text-violet-400 transition-colors">Batch Evaluation</h3>
                <p class="text-sm text-dark-400 mt-1">Run datasets with aggregated stats</p>
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
      <!-- Available Models -->
      <div class="card p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="section-title">Available Models</h3>
          <span class="badge-primary">{{ models.length }} models</span>
        </div>
        <div class="grid grid-cols-1 xs:grid-cols-2 gap-3">
          <div 
            v-for="model in models.slice(0, 6)" 
            :key="model.id"
            class="p-3 bg-dark-800/40 rounded-xl border border-dark-700/50 hover:border-dark-600/80 transition-colors"
          >
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-mistral-500/15 to-mistral-600/10 flex items-center justify-center flex-shrink-0">
                <CpuChipIcon class="w-4 h-4 text-mistral-400" />
              </div>
              <div class="min-w-0 flex-1">
                <h4 class="font-medium text-white text-sm truncate">{{ formatModelName(model.name) }}</h4>
                <p class="text-2xs text-dark-500 truncate mt-0.5">{{ model.id }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-if="models.length > 6" class="mt-4 text-center">
          <span class="text-xs text-dark-400">+ {{ models.length - 6 }} more models</span>
        </div>
      </div>

      <!-- Datasets -->
      <div class="card p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="section-title">Datasets</h3>
          <NuxtLink to="/datasets" class="text-sm text-mistral-400 hover:text-mistral-300 transition-colors">
            View all →
          </NuxtLink>
        </div>
        
        <div v-if="datasets.length > 0" class="space-y-3">
          <div 
            v-for="dataset in datasets.slice(0, 3)" 
            :key="dataset.name"
            class="flex items-center justify-between p-3 bg-dark-800/40 rounded-xl border border-dark-700/50"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-lg bg-dark-700/60 flex items-center justify-center flex-shrink-0">
                <DocumentTextIcon class="w-5 h-5 text-dark-400" />
              </div>
              <div class="min-w-0">
                <h4 class="font-medium text-white text-sm truncate">{{ dataset.name }}</h4>
                <p class="text-xs text-dark-400 truncate">{{ dataset.prompt_count }} prompts</p>
              </div>
            </div>
            <NuxtLink 
              :to="`/batch?dataset=${dataset.name}`"
              class="btn-secondary text-xs px-3 py-1.5 flex-shrink-0"
            >
              Run
            </NuxtLink>
          </div>
        </div>
        
        <div v-else class="text-center py-8">
          <DocumentTextIcon class="w-12 h-12 text-dark-600 mx-auto" />
          <p class="text-dark-400 mt-2 text-sm">No datasets available</p>
        </div>
      </div>
    </section>

    <!-- Key Features -->
    <section class="card p-5 sm:p-6 bg-gradient-to-br from-dark-900 to-dark-900/80">
      <h3 class="section-title mb-4">Key Features</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
            <ClockIcon class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h4 class="font-medium text-white text-sm">Latency Metrics</h4>
            <p class="text-xs text-dark-400 mt-0.5">TTFT, total time, tokens/sec</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center flex-shrink-0">
            <SparklesIcon class="w-5 h-5 text-sky-400" />
          </div>
          <div>
            <h4 class="font-medium text-white text-sm">Quality Scoring</h4>
            <p class="text-xs text-dark-400 mt-0.5">LLM-as-judge evaluation</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center flex-shrink-0">
            <ChartBarSquareIcon class="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h4 class="font-medium text-white text-sm">Variance Analysis</h4>
            <p class="text-xs text-dark-400 mt-0.5">Multi-run statistics</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
            <UserIcon class="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h4 class="font-medium text-white text-sm">Human Ratings</h4>
            <p class="text-xs text-dark-400 mt-0.5">Calibrate automated scores</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Getting Started CTA -->
    <section class="card p-6 sm:p-8 bg-gradient-to-r from-mistral-500/10 via-dark-900 to-mistral-600/10 border-mistral-500/20">
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-6">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-mistral-500/20 to-mistral-600/10 flex items-center justify-center flex-shrink-0">
          <RocketLaunchIcon class="w-7 h-7 text-mistral-400" />
        </div>
        <div class="flex-1">
          <h3 class="text-lg sm:text-xl font-bold text-white">Ready to start evaluating?</h3>
          <p class="text-dark-300 mt-1 text-sm sm:text-base">
            Run your first evaluation in seconds. Test prompts, compare models, and get actionable insights.
          </p>
        </div>
        <div class="flex gap-3 w-full sm:w-auto">
          <NuxtLink to="/evaluate" class="btn-primary flex-1 sm:flex-initial justify-center">
            Start Evaluation
          </NuxtLink>
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            class="btn-secondary flex-1 sm:flex-initial justify-center"
          >
            API Docs
          </a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { 
  BeakerIcon, 
  ScaleIcon, 
  ChartBarIcon, 
  DocumentTextIcon,
  CpuChipIcon,
  SparklesIcon,
  RocketLaunchIcon,
  ClockIcon,
  ChartBarSquareIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

const { checkHealth, getModels, getDatasets } = useApi()

const apiConnected = ref(false)
const models = ref<{ id: string; name: string; description: string }[]>([])
const datasets = ref<{ name: string; description?: string; prompt_count: number; categories: string[] }[]>([])

const totalPrompts = computed(() => 
  datasets.value.reduce((sum, d) => sum + d.prompt_count, 0)
)

const formatModelName = (name: string) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(async () => {
  try {
    const [health, modelsData, datasetsData] = await Promise.all([
      checkHealth(),
      getModels(),
      getDatasets()
    ])
    
    apiConnected.value = health.status === 'healthy'
    models.value = modelsData.models
    datasets.value = datasetsData
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// SEO
useSeoMeta({
  title: 'Dashboard',
  description: 'MistralMeter dashboard - Overview of your LLM evaluation platform with models, datasets, and quick actions.',
})
</script>
