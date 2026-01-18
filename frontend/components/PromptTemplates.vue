<template>
  <div class="card p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-white">Prompt Templates</h3>
      <button
        @click="showTemplates = !showTemplates"
        class="text-sm text-mistral-400 hover:text-mistral-300 transition-colors"
      >
        {{ showTemplates ? 'Hide' : 'Show' }}
      </button>
    </div>

    <div v-if="showTemplates" class="space-y-3">
      <div
        v-for="template in templates"
        :key="template.id"
        @click="$emit('select', template.prompt)"
        class="group cursor-pointer p-4 rounded-lg border border-dark-700/50 hover:border-mistral-500/40 hover:bg-dark-800/40 transition-all duration-200"
      >
        <div class="flex items-start gap-3">
          <component 
            :is="template.icon" 
            class="w-5 h-5 text-dark-400 group-hover:text-mistral-400 transition-colors flex-shrink-0 mt-0.5"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h4 class="font-medium text-white group-hover:text-mistral-400 transition-colors">
                {{ template.name }}
              </h4>
              <span 
                class="text-2xs px-2 py-0.5 rounded-full"
                :class="categoryClasses[template.category]"
              >
                {{ template.category }}
              </span>
            </div>
            <p class="text-sm text-dark-400 line-clamp-2">{{ template.prompt }}</p>
          </div>
          <ChevronRightIcon class="w-4 h-4 text-dark-600 group-hover:text-mistral-500 transition-colors flex-shrink-0" />
        </div>
      </div>
    </div>

    <!-- Quick filters -->
    <div v-if="showTemplates" class="mt-4 flex flex-wrap gap-2">
      <button
        v-for="category in categories"
        :key="category"
        @click="selectedCategory = selectedCategory === category ? null : category"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
        :class="selectedCategory === category 
          ? 'bg-mistral-500/20 text-mistral-400 border border-mistral-500/40'
          : 'bg-dark-800/60 text-dark-400 border border-dark-700/50 hover:border-dark-600'"
      >
        {{ category }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  CodeBracketIcon, 
  AcademicCapIcon, 
  SparklesIcon, 
  DocumentTextIcon,
  BeakerIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

interface Template {
  id: string
  name: string
  category: string
  prompt: string
  icon: any
}

const emit = defineEmits<{
  select: [prompt: string]
}>()

const showTemplates = ref(false)
const selectedCategory = ref<string | null>(null)

const allTemplates: Template[] = [
  {
    id: '1',
    name: 'Code Explanation',
    category: 'Code',
    prompt: 'Explain this Python code and identify potential improvements:\n\ndef process_data(items):\n    result = []\n    for item in items:\n        if item > 0:\n            result.append(item * 2)\n    return result',
    icon: CodeBracketIcon
  },
  {
    id: '2',
    name: 'Technical Explanation',
    category: 'Educational',
    prompt: 'Explain the concept of microservices architecture. Include:\n1. Definition and core principles\n2. Advantages vs monolithic architecture\n3. Common challenges and solutions\n4. A real-world example',
    icon: AcademicCapIcon
  },
  {
    id: '3',
    name: 'Creative Writing',
    category: 'Creative',
    prompt: 'Write a short story (200 words) about an AI that learns to appreciate art. The story should have:\n- A clear beginning, middle, and end\n- A moment of realization\n- Vivid imagery',
    icon: SparklesIcon
  },
  {
    id: '4',
    name: 'Document Summarization',
    category: 'Text',
    prompt: 'Summarize the following article in 3 bullet points:\n\n[Insert your article text here]\n\nFocus on the main ideas and key takeaways.',
    icon: DocumentTextIcon
  },
  {
    id: '5',
    name: 'API Design Review',
    category: 'Code',
    prompt: 'Review this REST API design and suggest improvements:\n\nGET /users/{id}\nPOST /users/create\nPUT /users/{id}/update\nDELETE /users/{id}/delete\n\nConsider: naming conventions, RESTful principles, and best practices.',
    icon: CodeBracketIcon
  },
  {
    id: '6',
    name: 'Reasoning Challenge',
    category: 'Reasoning',
    prompt: 'Solve this logic puzzle step by step:\n\nThree friends (Alice, Bob, Carol) each have a different pet (cat, dog, bird). \n- Alice doesn\'t have a dog\n- Bob is allergic to cats\n- Carol loves her bird\n\nWho has which pet? Show your reasoning.',
    icon: BeakerIcon
  },
  {
    id: '7',
    name: 'Sentiment Analysis',
    category: 'Text',
    prompt: 'Analyze the sentiment of this product review and categorize it as Positive, Negative, or Neutral. Explain your reasoning.\n\n"The product arrived on time and looks great, but the battery life is disappointing. Customer service was helpful though."',
    icon: DocumentTextIcon
  },
  {
    id: '8',
    name: 'Prompt Engineering',
    category: 'Educational',
    prompt: 'Explain prompt engineering best practices. Include:\n1. The anatomy of a good prompt\n2. Common techniques (few-shot, chain-of-thought, etc.)\n3. Examples of before/after prompt improvements\n4. Common pitfalls to avoid',
    icon: AcademicCapIcon
  }
]

const categories = ['All', 'Code', 'Educational', 'Creative', 'Text', 'Reasoning']

const categoryClasses = {
  'Code': 'bg-blue-500/10 text-blue-400',
  'Educational': 'bg-emerald-500/10 text-emerald-400',
  'Creative': 'bg-purple-500/10 text-purple-400',
  'Text': 'bg-yellow-500/10 text-yellow-400',
  'Reasoning': 'bg-pink-500/10 text-pink-400'
}

const templates = computed(() => {
  if (!selectedCategory.value || selectedCategory.value === 'All') {
    return allTemplates
  }
  return allTemplates.filter(t => t.category === selectedCategory.value)
})
</script>
