<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="showShortcuts"
        @click="showShortcuts = false"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <div
          @click.stop
          class="card max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto"
        >
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-white">Keyboard Shortcuts</h2>
            <button
              @click="showShortcuts = false"
              class="p-2 rounded-lg hover:bg-dark-700/50 transition-colors"
            >
              <XMarkIcon class="w-5 h-5 text-dark-400" />
            </button>
          </div>

          <div class="space-y-6">
            <!-- Evaluation shortcuts -->
            <div>
              <h3 class="text-sm font-semibold text-mistral-400 mb-3 uppercase tracking-wider">
                Evaluation
              </h3>
              <div class="space-y-2">
                <div class="flex items-center justify-between p-3 rounded-lg bg-dark-800/40 border border-dark-700/50">
                  <span class="text-sm text-dark-300">Run evaluation</span>
                  <div class="flex items-center gap-1">
                    <kbd class="kbd">Ctrl</kbd>
                    <span class="text-dark-500">+</span>
                    <kbd class="kbd">Enter</kbd>
                  </div>
                </div>
                <div class="flex items-center justify-between p-3 rounded-lg bg-dark-800/40 border border-dark-700/50">
                  <span class="text-sm text-dark-300">Clear prompt</span>
                  <div class="flex items-center gap-1">
                    <kbd class="kbd">Ctrl</kbd>
                    <span class="text-dark-500">+</span>
                    <kbd class="kbd">K</kbd>
                  </div>
                </div>
              </div>
            </div>

            <!-- Navigation shortcuts -->
            <div>
              <h3 class="text-sm font-semibold text-sky-400 mb-3 uppercase tracking-wider">
                Navigation
              </h3>
              <div class="space-y-2">
                <div class="flex items-center justify-between p-3 rounded-lg bg-dark-800/40 border border-dark-700/50">
                  <span class="text-sm text-dark-300">Open shortcuts menu</span>
                  <div class="flex items-center gap-1">
                    <kbd class="kbd">?</kbd>
                  </div>
                </div>
                <div class="flex items-center justify-between p-3 rounded-lg bg-dark-800/40 border border-dark-700/50">
                  <span class="text-sm text-dark-300">Close modal/menu</span>
                  <div class="flex items-center gap-1">
                    <kbd class="kbd">Esc</kbd>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tips -->
            <div class="p-4 rounded-lg bg-gradient-to-br from-mistral-500/10 to-mistral-600/5 border border-mistral-500/20">
              <div class="flex items-start gap-3">
                <LightBulbIcon class="w-5 h-5 text-mistral-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 class="text-sm font-semibold text-white mb-1">Pro Tips</h4>
                  <ul class="text-sm text-dark-300 space-y-1">
                    <li>• Use templates for quick prompt ideas</li>
                    <li>• Check cost calculator before running expensive tests</li>
                    <li>• Enable variance analysis for statistical confidence</li>
                    <li>• Your history is saved locally (last 50 evaluations)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Trigger button (fixed bottom-right) -->
  <button
    @click="showShortcuts = !showShortcuts"
    class="fixed bottom-4 right-4 z-40 p-3 rounded-full bg-gradient-to-br from-mistral-500 to-mistral-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
    title="Keyboard shortcuts (?)"
  >
    <QuestionMarkCircleIcon class="w-6 h-6" />
  </button>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { XMarkIcon, QuestionMarkCircleIcon, LightBulbIcon } from '@heroicons/vue/24/outline'

const showShortcuts = ref(false)

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    // Check if not in input
    const target = e.target as HTMLElement
    if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
      e.preventDefault()
      showShortcuts.value = !showShortcuts.value
    }
  }
  
  if (e.key === 'Escape') {
    showShortcuts.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.kbd {
  @apply px-2 py-1 text-xs font-mono font-semibold rounded bg-dark-700 border border-dark-600 text-dark-200 shadow-sm;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .card,
.modal-leave-active .card {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .card {
  transform: scale(0.95) translateY(-20px);
  opacity: 0;
}

.modal-leave-to .card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}
</style>
