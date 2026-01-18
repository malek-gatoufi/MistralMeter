<template>
  <div class="relative" :class="sizeClasses">
    <!-- Glow effect -->
    <div 
      class="absolute inset-0 rounded-full blur-xl opacity-30 transition-opacity duration-500"
      :class="glowColor"
    />
    
    <!-- Background circle -->
    <svg class="w-full h-full transform -rotate-90 relative">
      <defs>
        <linearGradient :id="`gradient-${uid}`" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" :stop-color="gradientStart" />
          <stop offset="100%" :stop-color="gradientEnd" />
        </linearGradient>
      </defs>
      
      <!-- Track -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        stroke="currentColor"
        :stroke-width="strokeWidth"
        class="text-dark-700/50"
      />
      
      <!-- Progress -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="`url(#gradient-${uid})`"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        class="transition-all duration-1000 ease-out"
      />
    </svg>
    
    <!-- Score text -->
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="font-bold text-white" :class="textSize">{{ score.toFixed(1) }}</span>
      <span class="text-dark-400" :class="subTextSize">/ 10</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

// Generate unique ID for gradient
const uid = Math.random().toString(36).substr(2, 9)

// Size configurations
const sizeConfig = computed(() => {
  const configs = {
    sm: { container: 'w-16 h-16', radius: 24, center: 32, strokeWidth: 5, text: 'text-lg', subText: 'text-2xs' },
    md: { container: 'w-24 h-24', radius: 40, center: 48, strokeWidth: 7, text: 'text-2xl', subText: 'text-xs' },
    lg: { container: 'w-32 h-32', radius: 52, center: 64, strokeWidth: 8, text: 'text-3xl', subText: 'text-sm' },
  }
  return configs[props.size]
})

const sizeClasses = computed(() => sizeConfig.value.container)
const radius = computed(() => sizeConfig.value.radius)
const center = computed(() => sizeConfig.value.center)
const strokeWidth = computed(() => sizeConfig.value.strokeWidth)
const textSize = computed(() => sizeConfig.value.text)
const subTextSize = computed(() => sizeConfig.value.subText)

const circumference = computed(() => 2 * Math.PI * radius.value)

const dashOffset = computed(() => {
  const progress = Math.min(props.score / 10, 1)
  return circumference.value * (1 - progress)
})

// Color based on score
const gradientStart = computed(() => {
  if (props.score >= 8) return '#10b981' // emerald-500
  if (props.score >= 6) return '#f59e0b' // amber-500
  return '#ef4444' // red-500
})

const gradientEnd = computed(() => {
  if (props.score >= 8) return '#34d399' // emerald-400
  if (props.score >= 6) return '#fbbf24' // amber-400
  return '#f87171' // red-400
})

const glowColor = computed(() => {
  if (props.score >= 8) return 'bg-emerald-500'
  if (props.score >= 6) return 'bg-amber-500'
  return 'bg-rose-500'
})
</script>
