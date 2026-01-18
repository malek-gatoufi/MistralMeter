import { ref, watch } from 'vue'

export interface EvaluationHistory {
  id: string
  prompt: string
  model: string
  timestamp: string
  score?: number
  temperature?: number
}

export function useLocalStorage() {
  const HISTORY_KEY = 'mistral-eval-history'
  const FAVORITES_KEY = 'mistral-eval-favorites'
  const MAX_HISTORY = 50

  // History
  const history = ref<EvaluationHistory[]>([])

  const loadHistory = () => {
    if (typeof window === 'undefined') return
    try {
      const stored = localStorage.getItem(HISTORY_KEY)
      if (stored) {
        history.value = JSON.parse(stored)
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const saveHistory = () => {
    if (typeof window === 'undefined') return
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value))
    } catch (error) {
      console.error('Failed to save history:', error)
    }
  }

  const addToHistory = (item: Omit<EvaluationHistory, 'id' | 'timestamp'>) => {
    const newItem: EvaluationHistory = {
      ...item,
      id: Math.random().toString(36).substring(7),
      timestamp: new Date().toISOString()
    }
    
    history.value.unshift(newItem)
    
    // Keep only last MAX_HISTORY items
    if (history.value.length > MAX_HISTORY) {
      history.value = history.value.slice(0, MAX_HISTORY)
    }
    
    saveHistory()
  }

  const clearHistory = () => {
    history.value = []
    saveHistory()
  }

  const removeFromHistory = (id: string) => {
    history.value = history.value.filter(item => item.id !== id)
    saveHistory()
  }

  // Favorites
  const favorites = ref<string[]>([])

  const loadFavorites = () => {
    if (typeof window === 'undefined') return
    try {
      const stored = localStorage.getItem(FAVORITES_KEY)
      if (stored) {
        favorites.value = JSON.parse(stored)
      }
    } catch (error) {
      console.error('Failed to load favorites:', error)
    }
  }

  const saveFavorites = () => {
    if (typeof window === 'undefined') return
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites.value))
    } catch (error) {
      console.error('Failed to save favorites:', error)
    }
  }

  const toggleFavorite = (prompt: string) => {
    const index = favorites.value.indexOf(prompt)
    if (index > -1) {
      favorites.value.splice(index, 1)
    } else {
      favorites.value.push(prompt)
    }
    saveFavorites()
  }

  const isFavorite = (prompt: string) => {
    return favorites.value.includes(prompt)
  }

  // Initialize
  loadHistory()
  loadFavorites()

  return {
    history,
    addToHistory,
    clearHistory,
    removeFromHistory,
    favorites,
    toggleFavorite,
    isFavorite
  }
}
