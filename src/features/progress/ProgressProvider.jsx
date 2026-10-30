import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'

const ProgressContext = createContext(null)

/**
 * Holds the progress state and persists it through a repository
 * (see lib/progress/storage.js). Renders nothing until the first load resolves.
 */
export function ProgressProvider({ repository, children }) {
  const [state, setState] = useState(null)
  const lastSaved = useRef(null)

  useEffect(() => {
    let alive = true
    repository.load().then((loaded) => {
      if (!alive) return
      lastSaved.current = JSON.stringify(loaded)
      setState(loaded)
    })
    const unsubscribe = repository.subscribe?.((external) => {
      lastSaved.current = JSON.stringify(external)
      setState(external)
    })
    return () => {
      alive = false
      unsubscribe?.()
    }
  }, [repository])

  useEffect(() => {
    if (state === null) return
    const serialized = JSON.stringify(state)
    if (serialized === lastSaved.current) return
    lastSaved.current = serialized
    repository.save(state)
  }, [state, repository])

  /** Apply a pure `(state) => state` update from lib/progress/state.js. */
  const update = useCallback((fn) => setState((prev) => (prev === null ? prev : fn(prev))), [])

  const value = useMemo(() => (state === null ? null : { state, update }), [state, update])
  if (value === null) return null

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
}

export function useProgressStore() {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('useProgressStore must be used inside <ProgressProvider>')
  return ctx
}
