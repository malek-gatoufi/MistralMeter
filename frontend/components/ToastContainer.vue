<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast-item rounded-lg shadow-lg p-4 border backdrop-blur-sm"
          :class="toastClasses[toast.type]"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <component :is="toastIcons[toast.type]" class="w-5 h-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium">{{ toast.message }}</p>
            </div>
            <button
              @click="removeToast(toast.id)"
              class="flex-shrink-0 text-current opacity-60 hover:opacity-100 transition-opacity"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { CheckCircleIcon, ExclamationCircleIcon, ExclamationTriangleIcon, InformationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useToast } from '~/composables/useToast'

const { toasts, removeToast } = useToast()

const toastClasses = {
  success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
  error: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
  warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
  info: 'bg-sky-500/10 border-sky-500/30 text-sky-400'
}

const toastIcons = {
  success: CheckCircleIcon,
  error: ExclamationCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}
</style>
