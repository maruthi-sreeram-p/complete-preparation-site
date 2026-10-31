import { emptyPractice, sanitizePractice } from './state.js'

/**
 * Practice repository, same interface as the progress repository (lib/progress/storage.js):
 * load(), save(state) and an optional subscribe(cb) for other open tabs.
 * A database-backed version can replace this without touching the UI.
 */
export function createPracticeRepository(key) {
  return {
    async load() {
      try {
        const raw = window.localStorage.getItem(key)
        return raw ? sanitizePractice(JSON.parse(raw)) : emptyPractice()
      } catch {
        return emptyPractice()
      }
    },

    save(state) {
      try {
        window.localStorage.setItem(key, JSON.stringify(state))
      } catch {
        // Storage full or unavailable (private mode): answers stay in memory for this session.
      }
    },

    subscribe(callback) {
      const onStorage = (event) => {
        if (event.key !== key) return
        try {
          callback(event.newValue ? sanitizePractice(JSON.parse(event.newValue)) : emptyPractice())
        } catch {
          callback(emptyPractice())
        }
      }
      window.addEventListener('storage', onStorage)
      return () => window.removeEventListener('storage', onStorage)
    },
  }
}
