<template>
  <div class="space-y-2">
    <div class="flex justify-between text-sm">
      <span class="text-dark-400">{{ label }}</span>
      <div class="flex gap-4">
        <span class="text-blue-400">A: {{ formatValue(valueA) }}{{ unit }}</span>
        <span class="text-mistral-400">B: {{ formatValue(valueB) }}{{ unit }}</span>
      </div>
    </div>
    <div class="flex gap-2 h-6">
      <!-- Bar A -->
      <div class="flex-1 flex items-center">
        <div 
          class="h-full rounded-l transition-all duration-500 flex items-center justify-end pr-2"
          :class="[
            'bg-blue-500',
            isABetter ? 'opacity-100' : 'opacity-50'
          ]"
          :style="{ width: `${(valueA / max) * 100}%` }"
        >
          <span v-if="isABetter && higherBetter !== undefined" class="text-xs text-white font-medium">
            {{ higherBetter ? '↑' : '↓' }} Better
          </span>
        </div>
      </div>
      
      <!-- Divider -->
      <div class="w-px bg-dark-600" />
      
      <!-- Bar B -->
      <div class="flex-1 flex items-center">
        <div 
          class="h-full rounded-r transition-all duration-500 flex items-center pl-2"
          :class="[
            'bg-mistral-500',
            isBBetter ? 'opacity-100' : 'opacity-50'
          ]"
          :style="{ width: `${(valueB / max) * 100}%` }"
        >
          <span v-if="isBBetter && higherBetter !== undefined" class="text-xs text-white font-medium">
            {{ higherBetter ? '↑' : '↓' }} Better
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string
  valueA: number
  valueB: number
  max: number
  unit?: string
  higherBetter?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  unit: '',
  higherBetter: undefined
})

const isABetter = computed(() => {
  if (props.higherBetter === undefined) return false
  return props.higherBetter 
    ? props.valueA > props.valueB 
    : props.valueA < props.valueB
})

const isBBetter = computed(() => {
  if (props.higherBetter === undefined) return false
  return props.higherBetter 
    ? props.valueB > props.valueA 
    : props.valueB < props.valueA
})

const formatValue = (val: number) => {
  if (val >= 1000) return (val / 1000).toFixed(1) + 'k'
  if (Number.isInteger(val)) return val
  return val.toFixed(1)
}
</script>
