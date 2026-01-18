<template>
  <div class="card p-6">
    <h3 class="text-lg font-semibold text-white mb-4">Variance Distribution</h3>
    
    <div class="space-y-6">
      <!-- Chart -->
      <div class="h-64 relative">
        <canvas ref="chartCanvas"></canvas>
      </div>

      <!-- Statistics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="text-center p-3 rounded-lg bg-dark-800/60 border border-dark-700/50">
          <div class="text-2xl font-bold text-white">{{ stats.mean.toFixed(2) }}</div>
          <div class="text-xs text-dark-400 mt-1">Mean</div>
        </div>
        <div class="text-center p-3 rounded-lg bg-dark-800/60 border border-dark-700/50">
          <div class="text-2xl font-bold text-sky-400">{{ stats.median.toFixed(2) }}</div>
          <div class="text-xs text-dark-400 mt-1">Median (P50)</div>
        </div>
        <div class="text-center p-3 rounded-lg bg-dark-800/60 border border-dark-700/50">
          <div class="text-2xl font-bold text-mistral-400">{{ stats.std_dev.toFixed(2) }}</div>
          <div class="text-xs text-dark-400 mt-1">Std Dev</div>
        </div>
        <div class="text-center p-3 rounded-lg bg-dark-800/60 border border-dark-700/50">
          <div class="text-2xl font-bold text-emerald-400">{{ stats.p95.toFixed(2) }}</div>
          <div class="text-xs text-dark-400 mt-1">P95</div>
        </div>
      </div>

      <!-- Range -->
      <div class="flex items-center justify-between text-sm">
        <div>
          <span class="text-dark-400">Min:</span>
          <span class="text-rose-400 font-semibold ml-2">{{ stats.min.toFixed(2) }}</span>
        </div>
        <div>
          <span class="text-dark-400">Max:</span>
          <span class="text-emerald-400 font-semibold ml-2">{{ stats.max.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Quality Badge -->
      <div class="flex items-center justify-center gap-2">
        <div
          class="px-4 py-2 rounded-lg border text-sm font-medium"
          :class="varianceQualityClasses[varianceQuality]"
        >
          {{ varianceQualityLabels[varianceQuality] }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import Chart from 'chart.js/auto'

interface Props {
  stats: {
    mean: number
    median: number
    std_dev: number
    min: number
    max: number
    p25: number
    p50: number
    p75: number
    p95: number
    coefficient_of_variation?: number
  }
  scores?: number[]
}

const props = defineProps<Props>()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const varianceQuality = computed(() => {
  const cv = props.stats.coefficient_of_variation || (props.stats.std_dev / props.stats.mean)
  if (cv < 0.05) return 'excellent'
  if (cv < 0.1) return 'good'
  if (cv < 0.2) return 'moderate'
  return 'poor'
})

const varianceQualityLabels = {
  excellent: '✨ Excellent Consistency',
  good: '✅ Good Consistency',
  moderate: '⚠️ Moderate Variance',
  poor: '❌ High Variance'
}

const varianceQualityClasses = {
  excellent: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
  good: 'bg-sky-500/10 border-sky-500/30 text-sky-400',
  moderate: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
  poor: 'bg-rose-500/10 border-rose-500/30 text-rose-400'
}

const createChart = () => {
  if (!chartCanvas.value) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  // Create histogram data
  const scores = props.scores || []
  const bins = 10
  const min = props.stats.min
  const max = props.stats.max
  const binSize = (max - min) / bins
  
  const histogram = new Array(bins).fill(0)
  scores.forEach(score => {
    const binIndex = Math.min(Math.floor((score - min) / binSize), bins - 1)
    histogram[binIndex]++
  })

  const labels = Array.from({ length: bins }, (_, i) => {
    const start = min + i * binSize
    return start.toFixed(1)
  })

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Frequency',
        data: histogram,
        backgroundColor: 'rgba(255, 94, 77, 0.5)',
        borderColor: 'rgba(255, 94, 77, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            title: (items) => {
              const index = items[0].dataIndex
              const start = min + index * binSize
              const end = start + binSize
              return `Score Range: ${start.toFixed(1)} - ${end.toFixed(1)}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.6)'
          }
        },
        y: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.6)',
            stepSize: 1
          }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.stats, () => {
  createChart()
}, { deep: true })
</script>
