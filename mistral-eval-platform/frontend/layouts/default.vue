<template>
  <div class="min-h-screen flex flex-col lg:flex-row">
    <!-- Mobile Header -->
    <header class="lg:hidden sticky top-0 z-50 glass border-b border-dark-700/50 safe-top">
      <div class="flex items-center justify-between px-4 py-3">
        <NuxtLink to="/" class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-mistral-500 to-mistral-600 flex items-center justify-center shadow-lg shadow-mistral-500/30">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="font-bold text-white">Mistral Bench</span>
        </NuxtLink>
        
        <button 
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="btn-icon"
          aria-label="Toggle menu"
        >
          <Bars3Icon v-if="!mobileMenuOpen" class="w-6 h-6" />
          <XMarkIcon v-else class="w-6 h-6" />
        </button>
      </div>

      <!-- Mobile Navigation Dropdown -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <nav v-if="mobileMenuOpen" class="px-4 pb-4 space-y-1">
          <NuxtLink
            v-for="item in navigation"
            :key="item.path"
            :to="item.path"
            @click="mobileMenuOpen = false"
            class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            :class="[
              $route.path === item.path 
                ? 'bg-mistral-500/20 text-mistral-400 border border-mistral-500/30' 
                : 'text-dark-300 hover:text-white hover:bg-dark-800/60'
            ]"
          >
            <component :is="item.icon" class="w-5 h-5" />
            <span class="font-medium">{{ item.name }}</span>
          </NuxtLink>
        </nav>
      </Transition>
    </header>

    <!-- Desktop Sidebar -->
    <aside class="hidden lg:flex w-72 flex-col bg-dark-900/60 backdrop-blur-xl border-r border-dark-700/50 sticky top-0 h-screen">
      <!-- Logo -->
      <div class="p-6 border-b border-dark-700/50">
        <NuxtLink to="/" class="flex items-center gap-3 group">
          <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-mistral-500 to-mistral-600 flex items-center justify-center shadow-lg shadow-mistral-500/30 group-hover:shadow-xl group-hover:shadow-mistral-500/40 transition-shadow">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 class="font-bold text-white text-lg">Mistral Bench</h1>
            <p class="text-xs text-dark-400">LLM Evaluation Platform</p>
          </div>
        </NuxtLink>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1.5 overflow-y-auto scrollbar-thin">
        <NuxtLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :class="[
            $route.path === item.path 
              ? 'bg-mistral-500/15 text-mistral-400 border border-mistral-500/30 shadow-sm' 
              : 'text-dark-300 hover:text-white hover:bg-dark-800/60'
          ]"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span class="font-medium">{{ item.name }}</span>
          <ChevronRightIcon 
            v-if="$route.path === item.path" 
            class="w-4 h-4 ml-auto text-mistral-400/60" 
          />
        </NuxtLink>
      </nav>

      <!-- API Status & Footer -->
      <div class="p-4 border-t border-dark-700/50 space-y-4">
        <!-- API Status -->
        <div class="card p-3.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div 
                class="w-2.5 h-2.5 rounded-full transition-colors duration-300"
                :class="apiStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"
              />
              <span class="text-sm font-medium" :class="apiStatus === 'connected' ? 'text-dark-200' : 'text-dark-400'">
                {{ apiStatus === 'connected' ? 'API Online' : 'API Offline' }}
              </span>
            </div>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank"
              class="text-xs text-dark-400 hover:text-mistral-400 transition-colors"
            >
              Docs →
            </a>
          </div>
        </div>

        <!-- Version -->
        <div class="text-center">
          <p class="text-2xs text-dark-500">
            ⚡ MistralMeter v2.0
          </p>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <!-- Desktop Header -->
      <header class="hidden lg:block sticky top-0 z-40 glass border-b border-dark-700/50">
        <div class="px-8 py-5">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-white">{{ pageTitle }}</h2>
              <p class="text-sm text-dark-400 mt-0.5">{{ pageDescription }}</p>
            </div>
            <div class="flex items-center gap-3">
              <a 
                href="https://github.com" 
                target="_blank"
                class="btn-icon"
                aria-label="GitHub"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
                </svg>
              </a>
              <a 
                href="http://localhost:8000/docs" 
                target="_blank"
                class="btn-secondary text-sm"
              >
                <ArrowTopRightOnSquareIcon class="w-4 h-4" />
                API Docs
              </a>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="p-4 sm:p-6 lg:p-8 safe-bottom">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { 
  HomeIcon, 
  BeakerIcon, 
  ScaleIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronRightIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const { checkHealth } = useApi()

// Mobile menu state
const mobileMenuOpen = ref(false)

// Close mobile menu on route change
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

// Navigation items
const navigation = [
  { name: 'Dashboard', path: '/', icon: HomeIcon },
  { name: 'Evaluate', path: '/evaluate', icon: BeakerIcon },
  { name: 'Compare', path: '/compare', icon: ScaleIcon },
  { name: 'Batch', path: '/batch', icon: ChartBarIcon },
  { name: 'Datasets', path: '/datasets', icon: DocumentTextIcon },
]

// Page metadata
const pageTitle = computed(() => {
  const current = navigation.find(n => n.path === route.path)
  return current?.name || 'MistralMeter'
})

const pageDescription = computed(() => {
  const descriptions: Record<string, string> = {
    '/': 'Overview of your LLM evaluation metrics',
    '/evaluate': 'Test a single prompt with detailed analysis',
    '/compare': 'Side-by-side model comparison',
    '/batch': 'Evaluate multiple prompts at once',
    '/datasets': 'Manage evaluation datasets',
  }
  return descriptions[route.path] || ''
})

// API status
const apiStatus = ref<'connected' | 'disconnected'>('disconnected')

onMounted(async () => {
  try {
    const health = await checkHealth()
    apiStatus.value = health.status === 'healthy' ? 'connected' : 'disconnected'
  } catch {
    apiStatus.value = 'disconnected'
  }
})

// SEO
useHead({
  title: pageTitle,
})
</script>
