<template>
  <span 
    class="inline-flex items-center gap-1.5 rounded-full font-semibold transition-all duration-200"
    :class="badgeClass"
  >
    <span 
      class="w-1.5 h-1.5 rounded-full"
      :class="dotClass"
    />
    {{ score.toFixed(1) }}
    <span v-if="showLabel" class="text-current/70 font-normal">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
interface Props {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showLabel: false
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  }
  return sizes[props.size]
})

const colorClasses = computed(() => {
  if (props.score >= 8) {
    return {
      badge: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
      dot: 'bg-emerald-400'
    }
  }
  if (props.score >= 6) {
    return {
      badge: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
      dot: 'bg-amber-400'
    }
  }
  return {
    badge: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
    dot: 'bg-rose-400'
  }
})

const badgeClass = computed(() => `${sizeClasses.value} ${colorClasses.value.badge}`)
const dotClass = computed(() => colorClasses.value.dot)

const label = computed(() => {
  if (props.score >= 8) return 'Excellent'
  if (props.score >= 6) return 'Good'
  return 'Needs Work'
})
</script>
