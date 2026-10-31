import { useEffect, useState } from 'react'

/** The value, but only after it has stopped changing for delayMs. */
export function useDebounce<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(id)   // typing again cancels the pending update
  }, [value, delayMs])

  return debounced
}
