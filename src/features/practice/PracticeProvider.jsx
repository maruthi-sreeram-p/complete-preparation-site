import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'

const PracticeContext = createContext(null)

/** Holds the practice state and saves it through a repository (see lib/practice/storage.js). */
export function PracticeProvider({ repository, children }) {
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

  /** Apply a pure `(state) => state` update from lib/practice/state.js. */
  const update = useCallback((fn) => setState((prev) => (prev === null ? prev : fn(prev))), [])

  const value = useMemo(() => (state === null ? null : { state, update }), [state, update])
  if (value === null) return null
  return <PracticeContext.Provider value={value}>{children}</PracticeContext.Provider>
}

export function usePractice() {
  const ctx = useContext(PracticeContext)
  if (!ctx) throw new Error('usePractice must be used inside <PracticeProvider>')
  return ctx
}
