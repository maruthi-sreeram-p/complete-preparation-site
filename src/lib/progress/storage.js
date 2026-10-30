import { emptyProgress, sanitizeProgress } from './state.js'

/**
 * Progress repository interface. The UI only ever talks to this, so a database
 * (REST API, Supabase, Firebase, ...) can replace LocalStorage by implementing:
 *
 *   load():            Promise<ProgressState>
 *   save(state):       Promise<void> | void
 *   subscribe?(cb):    () => void     // optional: call cb(newState) on external changes
 *
 * State shape and update rules live in ./state.js.
 */
export function createLocalStorageRepository(key) {
  return {
    async load() {
      try {
        const raw = window.localStorage.getItem(key)
        return raw ? sanitizeProgress(JSON.parse(raw)) : emptyProgress()
      } catch {
        return emptyProgress()
      }
    },

    save(state) {
      try {
        window.localStorage.setItem(key, JSON.stringify(state))
      } catch {
        // Storage full or unavailable (private mode): progress stays in memory for this session.
      }
    },

    /** Keeps several open tabs in sync. */
    subscribe(callback) {
      const onStorage = (event) => {
        if (event.key !== key) return
        try {
          callback(event.newValue ? sanitizeProgress(JSON.parse(event.newValue)) : emptyProgress())
        } catch {
          callback(emptyProgress())
        }
      }
      window.addEventListener('storage', onStorage)
      return () => window.removeEventListener('storage', onStorage)
    },
  }
}
